# FastAPIをインポート
from fastapi import FastAPI

# FastAPIの「インスタンス」を生成
app = FastAPI()


# パスオペレーションデコレータを定義
@app.get("/")
# パスオペレーションを定義
async def root():
    # コンテンツの返信
    return {"message": "Hello World"}