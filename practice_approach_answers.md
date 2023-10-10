# 解答アプローチ

## はじめに

本演習におけるFastAPIとUvicornの検証バージョンは以下です。

- fastapi: 0.103.2
- uvicorn: 0.23.2 

practiceNのブランチごとに解答例のソースコードがあります。
practice0、practice1については下記にも転記しています。

## (0) Hello World ! 

main.py
```
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
```

### 確認
@raw response http://127.0.0.1:8000/
@OpenAPIドキュメント http://127.0.0.1:8000/docs
@ReDocドキュメント http://127.0.0.1:8000/redoc
@APIスキーマ　http://127.0.0.1:8000/openapi.json



## (1) IPアドレスの種別を返答するAPIサービス

`ソースコード`
main.py
```
# FastAPIをインポート
from fastapi import FastAPI
# 自分で作成したカスタムライブラリから必要な関数をインポート
from myownlib import fetch_ipattr

# FastAPIの「インスタンス」を生成
app = FastAPI()

# パスオペレーションデコレータを定義
@app.get("/")
# パスオペレーションを定義
async def root():
    # コンテンツの返信
    return {"message": "Hello World"}

# IPアドレスの種別を取得するAPIエンドポイント
@app.get("/ipaddr/{ipstr}")
async def read_item(ipstr):
    ip_attr = fetch_ipattr(ipstr)
    return {"ipaddr": ipstr, "attr":ip_attr }
```

myownlib.py
```
# ipaddressモジュールからip_address関数をインポート　https://docs.python.org/ja/3.10/library/ipaddress.html
from ipaddress import ip_address

# ipaddressモジュールの定義属性での判別
def judge_ipattr(ipobj):
    version = ipobj.version
    if ipobj.is_reserved:
        return "Reserved IPv{} Address".format(version)
    elif ipobj.is_loopback:
        return "Loopback IPv{} Address".format(version)
    elif ipobj.is_link_local:
        return "Link Local IPv{} Address".format(version)
    elif ipobj.is_multicast:
        return "Multicast IPv{} Address".format(version)        
    elif ipobj.is_global:
        return "Global IPv{} Address".format(version)
    elif ipobj.is_private:
        return "Private IPv{} Address".format(version)
    elif ipobj.is_unspecified:
        return "Not Defined IPv{} Address".format(version)
    else:
        return "Unexpected IPv{} Address type. Beyond this APi coverage! Search in Google :)".format(version)

# ipaddressモジュールの定義属性での判別
def fetch_ipattr(ipstr):
    if "." in ipstr or ":" in ipstr:
        ipobj = ip_address(ipstr)
        try:
            return judge_ipattr(ipobj)
        except ValueError:
            return  "[Exception] Not IPv4 or IPv6 string format."
    else:
        return "[Error] Not IPv4 or IPv6 string format."
```

関連ライブラリファイルがカレントディレクトリにあり、main.pyのみpractice1/のものを使う場合
(fastapienv) % uvicorn practice1.main:app --reload
もしくは
(fastapienv)  % cd practice1
(fastapienv) % uvicorn main:app --reload



## (2) OAuth2を用いたユーザー認証
https://fastapi.tiangolo.com/ja/tutorial/security/first-steps/
https://fastapi.tiangolo.com/ja/tutorial/security/oauth2-jwt/

OAuth2が ユーザー名 や パスワード を送信するために、「フォームデータ」を扱うため追加インストール
$ pip install python-multipart
> Successfully installed python-multipart-0.0.5 six-1.16.0

JWTトークンの生成と検証を行うため
$ pip install python-jose
> Successfully installed ecdsa-0.18.0 pyasn1-0.4.8 python-jose-3.3.0 rsa-4.9

Bcryptアルゴリズムによるパスワードのハッシュ化のため
$ pip install passlib[bcrypt]
> Successfully installed passlib-1.7.4 bcrypt-4.0.1

関連ライブラリファイルがカレントディレクトリにあり、main.pyのみpractice2/のものを使う場合
(fastapienv) % uvicorn practice2.main:app --reload
または
(fastapienv)  % cd practice2
(fastapienv) % uvicorn main:app --reload

practice2/
main.py
myownlib.py

補足：仮DBのクレデンシャル
Username: johndoe 
Password: secret



## (3) DBを利用したユーザー登録とOAuth2を用いたユーザー認証
https://fastapi.tiangolo.com/ja/tutorial/sql-databases/

SQL操作ライブラリをインストール
$ pip install sqlalchemy
>Successfully installed greenlet-2.0.1 sqlalchemy-1.4.44

今回は簡易版として同じフォルダにSQLiteDBファイルで保存します

practice3/
__init__.py
crud.py
database.py
main.py
models.py
myownlib.py
schemas.py

テストデータ
{
  "email": "johndoe@example.com",
  "password": "secret",
  "username": "johndoe",
  "full_name": "John Doe"
}

**修正方針**
1. (2)作成の認証付きのアプリケーションにチュートリアルのsql-databasesテンプレートコードらをコピー追加し、main.pyのDB操作用のAPIエンドポイントを一つ一つ動作確認しながら修正する

2. [CREATE] DBを利用したユーザー登録の作成 `@app.post("/users/", response_model=schemas.User)`
    2.1 (2)のmain.pyからpydanticモデルらをschemas.pyへ移行
    2.2 (2)のmain.pyからpwd_contextらをcrud.pyに移行
    2.3 crud.dbのcreate_userのDBフィールド定義の追加、models.pyのusersテーブルの列定義追加
    2.4 is_activeの削除とdisabled = Column(Boolean, default=False)のdefaultをFalseに変更

3. [READ] DBに正く登録できているかを usersのAPIエンドポイントで確認　`@app.get("/users/", response_model=List[schemas.User])`

4. [READ] ログイン部分をfake_users_dbから2で作成したDBに変更　`@app.post("/token", response_model=schemas.Token)`
    4.1 main.pyからfake_users_db = {}を削除
    4.2 fake_users_dbとなっているのを関数の引数にdb: Session = Depends(get_db)を追加しdbに適宜変更
    4.3 crud.pyにget_password_by_usernameを追加
    4.4 main.pyのdef get_user(db, username: str):にget_password_by_usernameを反映
    これで、Authorize ログインができるようになる。

5. JWTトークンでの認証がうまくいくかを `@app.post("/users/", response_model=schemas.User)　および　@app.get("/ipaddr/{ipstr}")`にて確認


関連ライブラリファイルがカレントディレクトリにあり、main.pyのみpractice3/のものを使う場合
(fastapienv) % uvicorn practice3.main:app --reload
または
(fastapienv) % cd practice3
(fastapienv) % uvicorn main:app --reload



## (4) ユーザーの入力したIPアドレスのヒストリを登録し、それを返答するAPIサービス

スキーマの変更が必要になるため、./sql_app.dbを一度削除してください。本日の演習ではその後もスキーマを変更するたびに削除した方が良いです。

practice4/
__init__.py
crud.py
database.py
main.py
models.py
myownlib.py
schemas.py

**修正方針**
1. (3)で作成したmain.pyをベースに修正する
@app.get("/ipaddr/{ipstr}")
def search_ip_and_regist_history(ipstr, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)): 

2. (3)で作成したmodels.pyのItemテーブルをhistory用に利用する

3. (3)で作成したcrud.pyのdef create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):をhistory用に利用する
    itemはdictで直接 search_ip_and_regist_history から受け取るようにする

4. (3)で作成したschemas.pyのItemBase,ItemCreateにフィールド追加

Try & Errorでデバッグする
ここまででDBへのIPヒストリーの登録ができるようになる
最後は、自分のヒストリーを確認するAPIエンドポイントを作成する

5. main.pyに追加する
@app.get("/history/", response_model=List[schemas.Item])
def read_history(current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    history = crud.retrieve_user_history(db=db, user_id=current_user.id)
    return history

6. crud.pyに追加する
def retrieve_user_history(db: Session, user_id: int):
    return db.query(models.Item).filter(models.Item.owner_id == user_id).all()

関連ライブラリファイルがカレントディレクトリにあり、main.pyのみpractice4/のものを使う場合
(fastapienv) % uvicorn practice4.main:app --reload
または
(fastapienv) % cd practice4
(fastapienv) % uvicorn main:app --reload




## (5) To be secure: 堅牢化への取り組み

Practice 4の長谷川の完成版を題材に、API堅牢化ポイントを発見し、堅牢化を実装してください。

Step 1: 
    実装上の不備がありエラーになるAPIエンドポイントが存在します。探してそのAPIエンドポイントを無効化してください。

    ```
    (不幸中の幸い！これができると他のユーザーのアイテムへの書き込みができることになってました)
    理由：itemをdictに変更したのでエラーになる　@app.post("/users/{user_id}/items/", response_model=schemas.Item)
    db_item = models.Item(owner_id=user_id, ipaddress=item.get("ipstr"), ip_attr=item.get("ip_attr")) # **item.dict(), を削除
        AttributeError: 'ItemCreate' object has no attribute 'get'
    ```

Step 2:
    /users/のAPIエンドポイントには実装上の不備があります。有効化したまま堅牢化してください。

    ```
    方針例：認証と認可の追加(管理者アカウントのみ認証後に閲覧可能とする認可を与える) 
    
    不備 API2:2023 Broken Authentication 認証が弱いまたはついていない。
    + 認証で登録ユーザーのみからしかアクセスできないようにする
    + def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):

    不備 API5:2023 BFLA ログインしたユーザーがすべてのユーザーの情報にアクセスできてしまう
    + 認可で管理者ユーザーからしかアクセスできないようにする
    + 簡単な暫定案の一例: user_id = 1の一番最初に登録したユーザーをadminにすることを実装した
    [!] ベストはDBの列に管理者フラグをつけて管理し、ソースコードから管理者が特定されないようにすること
    ```


Step 3:
    /items/のAPIエンドポイントには実装上の不備があります。全体最適化により堅牢化してください。

    ```
    /items/のAPIエンドポイントに認証と認可の追加が基本。(API1,API2,API5)
    全ユーザーのitemsリストは/users/にも含まれており、
    ログインユーザーのitemsリストは/history/と実装が被っているので、ここでは/items/のAPIエンドポイントを"無効化"するのが理想と考えます。
    ```


Step 4:
    /users/{userid}のAPIエンドポイントには実装上の不備があります。全体最適化により堅牢化してください。

    ```
    不備 API1:2023 BOLA -> userBの認可情報でuserAの情報が閲覧できてしまう問題がある。ログインユーザーが自分のIDの情報しか見えないようにする。
    不備 API2:2023 Broken Authentication -> 認証が弱いまたはついていない。認証で登録ユーザーのみからしかアクセスできないようにする
    の二つを実装。
    もしくは、/users/meと同じになるので"無効化"でも良いが、/users/meにはitemsが載ってきていないので無効化する場合はitemsフィールドをRDBからget_userで取得する必要がある
    ```

Step 5:
    /history/のAPIエンドポイントには設計上の弱点があります。有効化したまま堅牢化してください。

    ```
    弱点 API4:2023 Unrestricted Resource Comsumption -> Listで返すときは上限を設定しバッファオーバーフローを防ぐ　def retrieve_user_history(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    if limit > 100:
        raise HTTPException(status_code=400, detail="Exceed the maximum limit !")    

    一般的には、検索フィルターを実装したり、ページングでデータを連続的に処理しますが、本解説ではそこまで実装していません。
    別案：IPアドレスでのAPIエンドポイントへのクエリ回数の制限など
    ```

Step 6:
    現在の認証フォームには実装上の弱点があります。弱点を探し、堅牢化してください。

    ```
    弱点 API2:2023 Broken Authentication -> UserDBのユニークキーが emailにもかからわずusernameとパスワードでのログインになっている
    現時点では異なるメールアドレスで同じユーザー名を利用できてしまい、パスワードも同じである場合に意図しない別のユーザーの情報を表示できてしまう可能性がある。
    修正案1. usernameとパスワードでのログインから、emailとパスワードでのログインに変更する。
    修正案2. usernameをunique=Trueのユニークキーにする

    複垢の作成リスクを下げるにはemailをログインフォームに利用するほうが、モニタリングしやすいため、今回は修正案1を利用した。

    main.py
    def get_user(db, email: str):
        user_obj = crud.get_user_by_email(db,email)
    など他token周りの全てに反映

    schemas.py
    class TokenData(BaseModel):
        email: Union[str, None] = None
    ```

Optional Step:
    あと少なくとも１ヶ所に実装上の弱点があります。それはどこでしょうか？

    ```
    ソースコードへの秘密鍵のハードコーディング。GitHubなどで秘密鍵が漏洩し、かつMITMやSniffingで盗聴されたときにJWTトークンからユーザー名を復号できてしまう。
        該当箇所　# openssl rand -hex 32 を実行して、JWTトークンの署名に使用されるランダムな秘密鍵を登録する
        SECRET_KEY = "58c915fde18fbdd00c875f9edca8eec880504e745bcb6791921203c7dd56ebbc"
        OSの環境変数やkeyringなどを利用してソースコード外に出すこと！

    API8:2023 Security misconfiguration -> HTTPSになっておらずTLS/SSL対応がなされていない

    API10:2019 ロギングが十分に取られていない不備もあります
    ロギングはuvicornが記録するアクセスログをダンプするほかにMiddlewareやAPIRouterの機能でカスタム実装できます
    参考：https://blog.jicoman.info/2021/01/how-to-logging-request-and-response-body-by-fastapi/
    しかし2023年版のAPI8:2023では、不要なロギングやエラーメッセージは出力しないほうがよいという意見もあります。

    正直、この演習用APIサーバーに対する脆弱性や不備は他にももっと他にもあるはずです・・・
    JWTによる認証部分など https://www.rfc-editor.org/rfc/rfc8725.html


    ```

関連ライブラリファイルがカレントディレクトリにあり、main.pyのみpractice5/のものを使う場合
(fastapienv)  % uvicorn practice5.main:app --reload
または
(fastapienv)  % cd practice5
(fastapienv)  % uvicorn main:app --reload

**注意：Practice5の解答コードではAuthrizeのusernameにはemailを入力すること**
Happy API Security :) !


## Appendix

テストデータ
{
  "email": "johndoe@example.com",
  "password": "secret",
  "username": "johndoe",
  "full_name": "John Doe"
}

{
  "email": "test@example.com",
  "password": "test",
  "username": "test",
  "full_name": "Test User"
}


以上です。
お疲れさまでした。

