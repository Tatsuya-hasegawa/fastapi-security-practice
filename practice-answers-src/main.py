from datetime import datetime, timedelta
from typing import Union, List  # List追加
# FastAPIをインポート
from fastapi import Depends, FastAPI, HTTPException, status
# ユーザー認証に必要な関数のインポート
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

# Databaseライブラリのインポート
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

# 自分で作成したカスタムライブラリから必要な関数をインポート
from myownlib import fetch_ipattr

# openssl rand -hex 32 を実行して、JWTトークンの署名に使用されるランダムな秘密鍵を登録
SECRET_KEY = "58c915fde18fbdd00c875f9edca8eec880504e745bcb6791921203c7dd56ebbc"
# JWTトークンの署名に使用するアルゴリズム
ALGORITHM = "HS256"
# JWT トークンの有効期限 30分
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ここで、tokenUrl="token"は、まだ作成していない相対URLtokenを指します。相対URLなので、./tokenと同じです。
# 相対URLを使っているので、APIがhttps://example.com/にある場合、https://example.com/tokenを参照します。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# oauth2_schemeはOAuth2PasswordBearerのインスタンスです。oauth2_scheme(some, parameters)のように呼び出し可能であるためDependsと一緒に使う

# データベーステーブルの作成
models.Base.metadata.create_all(bind=engine)

# FastAPIの「インスタンス」を生成
app = FastAPI()

# Dependency: データベースセッションを呼び出す
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DBからユーザー情報の取得
def get_user(db, username: str):
    user_obj = crud.get_user_by_username(db,username)
    #if username in db:
    #    user_dict = db[username]
    #    return schemas.UserInDB(**user_dict)
    try:
        user_dict = user_obj.__dict__
        return schemas.UserInDB(**user_dict)
    except:
        return None
    
# フォームで受け取ったユーザー名とパスワードをDBと照合して登録されているユーザーかどうかを認証する
def authenticate_user(real_db, username: str, password: str):
    user = get_user(real_db, username)
    if not user:
        return False
    if not crud.verify_password(password, user.hashed_password):
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
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)): # asyncを外して、db: Session = Depends(get_db)を追加
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
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# アクティブユーザーかどうかを確認する関数
async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

############# (0) Hello World ! ###########
# パスオペレーションデコレータを定義
@app.get("/")
# パスオペレーションを定義
async def root():
    # コンテンツの返信
    return {"message": "Practice4:  IP Address attribute search with OAuth2 JWT and SQLite DB. In addition, registering and retrieving the IP search history"}


############ (1) IP種別チェック用 & (4) History登録 #############
# IPアドレスの種別を取得するAPIパス
@app.get("/ipaddr/{ipstr}")
def search_ip_and_regist_history(ipstr, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):   # 関数名をread_itemから変更 
    ip_attr = fetch_ipattr(ipstr)
    result_item = crud.create_user_item(db=db, item={"ipstr":ipstr,"ip_attr":ip_attr}, user_id=current_user.id)
    print(result_item)
    return {"ipaddr": ipstr, "attr":ip_attr, "owner": current_user.username } 


############## (2) 認証用 #################
# ユーザー名とパスワードを入力してJWTトークンを取得するAPI認証パス
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)): # asyncを外して、db: Session = Depends(get_db)を追加
    user = authenticate_user(db, form_data.username, form_data.password)
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
@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(current_user: schemas.User = Depends(get_current_active_user)):
    return [{"item_id": "Congrats! Practice 4 has been finished !", "owner": current_user.username}]

############ (3) DB操作用 #############
# 以下では、DBの応答を待つ必要があるのでasyncをつけていない。また本演習はAsync SQLに対応させていない　参考　https://fastapi.tiangolo.com/ja/advanced/async-sql-databases/ https://fastapi.tiangolo.com/ja/async/#very-technical-details
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

############ (4) IPヒストリー取得用 #############
@app.get("/history/", response_model=List[schemas.Item])
def read_history(current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    history = crud.retrieve_user_history(db=db, user_id=current_user.id)
    return history
