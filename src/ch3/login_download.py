# 作詞掲示板にログインしてCSVファイルをダウンロードする
import time
from playwright.sync_api import sync_playwright

# ログインページのURL
LOGIN_URL = "https://uta.pw/sakusibbs/users.php?action=login"
USER_ID = "JS-TESTER"
PASSWORD = "ipCU12ySxI"

with sync_playwright() as p:
    # 可視状態でブラウザを起動 --- (※1)
    browser = p.chromium.launch(headless=False)
    # ダウンロードを許可する --- (※2)
    context = browser.new_context(accept_downloads=True)
    page = browser.new_page()

    # ログインページへ移動 --- (※3)
    page.goto(LOGIN_URL)
    print("ログインページに移動しました")
    # ログイン情報を挿入
    page.fill('input#user', USER_ID)
    page.fill('input#pass', PASSWORD)
    # フォームの送信ボタンをクリック --- (※4)
    page.click('input[type="submit"]')
    print("ログイン情報を送信しました")
    page.wait_for_load_state("networkidle")
    # マイページへ移動 --- (※5)
    page.get_by_text("★マイページ").click()
    print("マイページへ移動しました")
    page.wait_for_load_state("networkidle")
    # CSVファイルをダウンロード --- (※6)
    with page.expect_download() as download_info:
        page.click("a:has-text('一覧をCSVでダウンロード')")
    # ファイルを保存 --- (※7)
    download = download_info.value
    download.save_as("mypage-mmlist.csv")
    print("CSVファイルをダウンロードしました")
    # ブラウザを閉じる --- (※8)
    time.sleep(5)  # 少し待ってから閉じる
    browser.close()
