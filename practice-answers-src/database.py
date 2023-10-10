from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# database.py: 初期化定義コンポーネント

# データベースURLの定義
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# データベースエンジンの作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# データベースを操作するセッションのインスタンスの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベースのインスタンスを作成
Base = declarative_base()