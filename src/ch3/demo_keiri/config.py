"""設定ファイル"""
# ログイン情報 --- (※1)
LOGIN_URL = "https://api.aoikujira.com/demo_keiri/login.php"
USER_ID = "admin"
PASSWORD = "pOuIohVNS4aDOY8i"
# HTMLセレクタ --- (※2)
USERNAME_SELECTORS = [
    '#username',
    '[name="username"]',
    'input[type="text"]'
]
PASSWORD_SELECTORS = [
    '#password',
    '[name="password"]',
    'input[type="password"]'
]
SUBMIT_SELECTORS = [
    'button[type="submit"]',
    'button',
    'input[type="submit"]'
]
# CSVのカラム --- (※3)
CSV_FIELDNAMES = [
    '取引ID',
    '日時',
    '商品ID',
    '商品名',
    '単価',
    '数量',
    '小計',
    '支払い方法'
]
