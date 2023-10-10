# FastAPIをインポート
from fastapi import FastAPI
# 自分で作成したカスタムライブラリから必要な関数をインポート
from myownlib import fetch_ipattr

# FastAPIの「インスタンス」を生成
app = FastAPI()

############# (0) Hello World ! ROOTパス ###########
# パスオペレーションデコレータを定義
@app.get("/")
# パスオペレーションを定義
async def root():
    # コンテンツの返信
    return {"message": "Practice 1: IP Address attribute search with no Auth."}

############ (1) IP種別チェック用 #############
# IPアドレスの種別を取得するAPIパス
@app.get("/ipaddr/{ipstr}")
async def read_item(ipstr):
    ip_attr = fetch_ipattr(ipstr)
    return {"ipaddr": ipstr, "attr":ip_attr }