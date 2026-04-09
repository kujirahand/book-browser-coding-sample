from pathlib import Path
import flask
import webview

# ファイルのパスを設定
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
INDEX_HTML = STATIC_DIR / "index.html"

# JavaScriptから呼び出すPythonのAPIクラス --- (*1)
class PythonApi:

    def open_file(self) -> str:
        """ファイルを選んでその内容を返す""" # --- (*2)
        win = webview.windows[0]
        path = self._pick_path(win.create_file_dialog(webview.FileDialog.OPEN))
        if path:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return "ファイルが選択されませんでした"

    def save_file(self, content: str) -> str:
        """内容をファイルに保存する""" # --- (*3)
        win = webview.windows[0]
        path = self._pick_path(win.create_file_dialog(webview.FileDialog.SAVE))
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return "ファイルが保存されました"
        return "ファイルが選択されませんでした"

    def _pick_path(self, dialog_result) -> str | None:
        """create_file_dialogの戻り値からパス文字列を取り出す"""
        if not dialog_result:
            return None
        if isinstance(dialog_result, str):
            return dialog_result
        return dialog_result[0]

def on_start():
    """PythonからJavaScriptを呼び出す""" # --- (*4)
    win = webview.windows[0]
    win.evaluate_js('showStatus("Python側の準備完了")')

# Flaskサーバーを作成して、index.htmlを返す --- (*5)
server = flask.Flask(__name__, static_folder=str(STATIC_DIR))

@server.route("/")
def index():
    """ルートにアクセスがあったときにindex.htmlを返す"""
    return flask.send_file(INDEX_HTML)

# pywebviewのウィンドウを作成して、Flaskサーバーを表示する --- (*6)
webview.create_window(
    "pywebviewでテキストエディタ",
    server,
    js_api=PythonApi(),
    width=800,
    height=600,
)
webview.start(on_start)
