from sqlalchemy.orm import Session

import models, schemas

# ======== (2) main.pyより　============
from passlib.context import CryptContext

# パスワードのハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# パスワードハッシュの取得
def get_password_hash(password):
    return pwd_context.hash(password)

# パスワードの合致確認
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# ====================================
#データベースのデータを操作するための再利用可能なコンポーネント
# CRUDは、Create, Read, Update, Deleteからきています。このファイルにあるのはCreateとReadのみです。

# ユーザーIDを用いて一人のユーザー情報を取得
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# ユーザーのメールアドレスを用いて、一人のユーザー情報を取得
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# [追加]ユーザーのユーザー名を用いて、一人のユーザー情報を取得
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# 複数のユーザー情報を取得
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

#　ユーザー作成
def create_user(db: Session, user: schemas.UserCreate):
    db_hashed_password = get_password_hash(user.password) # user.password + "notreallyhashed" からの修正
    db_user = models.User(email=user.email, hashed_password=db_hashed_password, username=user.username, full_name=user.full_name) # DBフィールド追加
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 複数のアイテム情報を取得
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

#　ユーザーのアイテム作成
def create_user_item(db: Session, item: dict, user_id: int): # itemの内容はPOSTデータではなく、ip search のAPIパスの結果からdictで受けとる
    db_item = models.Item(owner_id=user_id, ipaddress=item.get("ipstr"), ip_attr=item.get("ip_attr")) # **item.dict(), を削除
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# [追加] ユーザーのIPサーチヒストリーの取得
def retrieve_user_history(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Item).filter(models.Item.owner_id == user_id).offset(skip).limit(limit).all()
