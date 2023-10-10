from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# database.pyからBaseクラスをインポート
from database import Base

# SQLAlchemyのモデルを作成するコンポーネント
# SQLAlchemy では、データベースとやりとりするこれらのクラスとインスタンス を指して、"モデル "という用語を利用
# しかし、Pydantic は "モデル" という用語を、データの検証、変換、文書化のクラスやインスタンスという、別のものを指すのにも使ってい流ので混同に注意

#  usersテーブルの定義
class User(Base):
    __tablename__ = "users"

    # 列カラムの定義
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    username = Column(String)
    full_name = Column(String)
    disabled = Column(Boolean, default=False)
    #is_active = Column(Boolean, default=True)

    # リレーションシップの定義（Itemクラスとownerの列で連結）
    items = relationship("Item", back_populates="owner")

# itemsテーブルの定義
class Item(Base):
    __tablename__ = "items"

    # 列カラムの定義
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # リレーションシップの定義（Userクラスとitemsの列で連結）
    owner = relationship("User", back_populates="items")