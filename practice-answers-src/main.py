from datetime import datetime, timedelta
from typing import Union
# FastAPIをインポート
from fastapi import Depends, FastAPI, HTTPException, status
# ユーザー認証に必要な関数のインポート
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# 自分で作成したカスタムライブラリから必要な関数をインポート
from myownlib import fetch_ipattr

# openssl rand -hex 32 を実行して、JWTトークンの署名に使用されるランダムな秘密鍵を登録
SECRET_KEY = "58c915fde18fbdd00c875f9edca8eec880504e745bcb6791921203c7dd56ebbc"
# JWTトークンの署名に使用するアルゴリズム
ALGORITHM = "HS256"
# JWT トークンの有効期限 30分
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 仮DB
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

# レスポンスのトークンエンドポイントで使用するPydanticモデルを定義
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

# パスワードのハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ここで、tokenUrl="token"は、まだ作成していない相対URLtokenを指します。相対URLなので、./tokenと同じです。
# 相対URLを使っているので、APIがhttps://example.com/にある場合、https://example.com/tokenを参照します。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# oauth2_schemeはOAuth2PasswordBearerのインスタンスです。oauth2_scheme(some, parameters)のように呼び出し可能であるためDependsと一緒に使う

# FastAPIの「インスタンス」を生成
app = FastAPI()

# パスワードの合致確認
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# パスワードハッシュの取得(not in use)
def get_password_hash(password):
    return pwd_context.hash(password)

# DBからユーザー情報の取得
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

# フォームで受け取ったユーザー名とパスワードをDBと照合して登録されているユーザーかどうかを認証する
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 新しいアクセストークンを生成するユーティリティ関数
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWTトークンのユーザー情報を取得する関数
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# アクティブユーザーかどうかを確認する関数
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

############# (0) Hello World ! ROOTパス ###########
# パスオペレーションデコレータを定義
@app.get("/")
# パスオペレーションを定義
async def root():
    # コンテンツの返信
    return {"message": "Practice 2: IP Address attribute search with OAuth2 JWT."}

############ (1) IP種別チェック用 #############
# IPアドレスの種別を取得するAPIパス
@app.get("/ipaddr/{ipstr}")                                                         
async def read_item(ipstr,current_user: User = Depends(get_current_active_user)):   # 追記
    ip_attr = fetch_ipattr(ipstr)
    return {"ipaddr": ipstr, "attr":ip_attr, "owner": current_user.username }       # 追記 

############## (2) 認証用 #################
# ユーザー名とパスワードを入力してJWTトークンを取得するAPI認証パス
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 受け取ったJWTトークンを復号して検証し、現在のユーザーを返すAPIパス
@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Congrats! Practice 2 has been finished!", "owner": current_user.username}]