from playwright.sync_api import sync_playwright

# 対象となるURL
target_url = "https://kujirahand.com/"

with sync_playwright() as p:
    # ブラウザ起動（ヘッドレス） --- (*1)
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    # 対象ページを開く --- (*2)
    page.goto(target_url)
    # タイトル取得 --- (*3)
    title = page.title()
    print("タイトル:", title)
    # h1要素取得
    h1 = page.query_selector("h1")
    if h1:
        print("見出し:", h1.inner_text())
    browser.close()
