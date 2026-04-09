import flask
import webview

# Flaskのサーバーを作成 --- (*1)
server = flask.Flask(__name__)

# Flaskでルートのエンドポイントを定義 --- (*2)
@server.route("/")
def index():
    return "<h1>pywebviewでFlaskサーバーを表示</h1>"

# pywebviewでFlaskサーバーを登録 --- (*3)
webview.create_window("pywebview_flask", server)
# pywebviewを起動 --- (*4)
webview.start()
