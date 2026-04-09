# 作詞掲示板のユーザー作品一覧を取得する
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

# 取得したいユーザーのIDを指定してURLを組み立てる
USER_ID = 1
USER_URL = f"https://uta.pw/sakusibbs/users.php?user_id={USER_ID}"

with sync_playwright() as p:
    # ブラウザを起動 --- (※1)
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    # 対象ページへ移動 --- (※2)
    page.goto(USER_URL)
    # 特定の要素を取得 --- (※3)
    mmlist = page.query_selector("#mmlist")
    items = mmlist.query_selector_all("li")
    # 各作品のタイトルとURLを表示 --- (※4)
    for item in items:
        # リンクを取得 --- (※5)
        link = item.query_selector("a")
        title = link.inner_text()
        href = link.get_attribute("href")
        # URLを絶対URLに変換 --- (※6)
        base_url = page.url   # 今開いているページのURL
        url = urljoin(base_url, href)
        print(f"{title}: {url}")
    # ブラウザを閉じる --- (※7)
    browser.close()
