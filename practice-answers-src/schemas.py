from typing import List, Union

from pydantic import BaseModel

# Pydanticのモデルの定義モジュール

# SQLAlchemy のモデルと Pydantic のモデルを混同しないように、models.py に SQLAlchemy のモデル、schemas.py に Pydantic のモデルを記述することにします。
# これらの Pydantic モデルは、多かれ少なかれ「スキーマ」（有効なデータの形） を定義します。
# これは、両方を使うときの混乱を避けるのに役立ちます。

class ItemBase(BaseModel):
    # 型の宣言
    ipaddress: str
    ip_attr: str
    #title: str
    #description: Union[str, None] = None

# [Optional] Itemスキーマについては、APIのPOSTで受け取らない仕様のため、実際は使わないが、練習がてら定義します。
class ItemCreate(ItemBase):
    pass

# APIからItemデータを返すときに使用するPydanticモデル（スキーマ）を作成
class Item(ItemBase):
    # 型の宣言
    id: int
    owner_id: int
    ipaddress: str
    ip_attr: Union[str, None] = None

    class Config:
        # 値の代入
        orm_mode = True
        # orm_mode がなければ、もしパス操作から SQLAlchemy のモデルを返したとしても、リレーションシップのデータは含まれない。

class UserBase(BaseModel):
    email: str

# ユーザー作成時のリクエストボディの追加フィールドたち    
class UserCreate(UserBase):
    password: str
    username: str
    full_name: str

# APIからUserデータを返すときに使用するPydanticモデル（スキーマ）を作成
class User(UserBase):
    # 型の宣言
    id: int
    #is_active: bool
    items: List[Item] = []
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

    class Config:
        # 値の代入
        orm_mode = True
        # orm_mode がなければ、もしパス操作から SQLAlchemy のモデルを返したとしても、リレーションシップのデータは含まれない。

class UserInDB(User):
    hashed_password: str

# (認証用) レスポンスのトークンエンドポイントで使用するPydanticモデルを定義
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Union[str, None] = None
