"""為替サイトにログインして4通貨の情報を得るプログラム"""
import asyncio  # asyncioを使うために必要なモジュール --- (※1)
import csv
from urllib import parse
from playwright.async_api import async_playwright  # Playwrightの非同期APIを使うために必要なモジュール --- (※2)

# 為替サイト(ログインページ)のURL --- (※3)
TOP_PAGE_URL = "https://api.aoikujira.com/kawase/login.php"
# ログイン情報
LOGIN_ID = "guest"
LOGIN_PASSWORD = "0u1eirYwfkuqmRF0"
# 取得する通貨のリスト --- (※4)
CURR_LIST = ["USD", "SGD", "EUR", "MYR"]
CSV_FILE = "kawase_data.csv" # CSVファイル名

async def main():
    """メイン処理"""  #--- (※5)
    async with async_playwright() as p:
        # ブラウザを起動して新しいページを開く
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # ログインして為替情報を取得する処理を実行 --- (※6)
            await login(page)
            links = await get_links(page)
            kawase_data = await get_kawase_info(page, links)
            await save_to_csv(kawase_data)
            print("[INFO] 処理完了")
        except Exception as e:
            print(f"[ERROR] 予期しないエラー: {e}")
        finally:
            await browser.close()

async def login(page):
    """ログインページにアクセスして認証を行う"""  # --- (※7)
    # ログインページを開く
    await page.goto(TOP_PAGE_URL, wait_until="networkidle")
    print(f"[INFO] ログインページにアクセス: {TOP_PAGE_URL}")
    
    # JavaScriptによる要素の生成を待つ
    await page.wait_for_selector('input[name="id"]', state="visible")
    
    # ログイン情報を入力
    await page.fill('input[name="id"]', LOGIN_ID)
    await page.fill('input[name="pw"]', LOGIN_PASSWORD)
    print("[INFO] ログイン情報を入力")
    
    # ログインボタンをクリックして、ナビゲーションまたはレスポンスを待つ
    async with page.expect_navigation(wait_until="networkidle", timeout=10000):
        await page.click('input[type="submit"]')
    print("[INFO] ログイン完了")
    await asyncio.sleep(1)  # サーバー負荷軽減のために少し待つ

async def get_links(page):
    """ログイン後のページから為替レート情報へのリンクを取得"""  # --- (※8)
    # 現在のURLを確認
    print(f"[INFO] 現在のURL: {page.url}")
    # 「情報を見る」というリンクがあるか確認
    link = await page.query_selector('a:has-text("情報を見る")')
    if link:
        await link.click()
        await page.wait_for_load_state("networkidle")
        print("[INFO] 「情報を見る」リンクをクリック")
        await asyncio.sleep(1)  # サーバー負荷軽減のために少し待つ
    else:
        raise IOError("「情報を見る」リンクが見つかりません")
    # リンク一覧を得る --- (※9)
    links = []
    for curr in CURR_LIST:
        link = await page.query_selector(f'a:has-text("{curr}")')
        if link:
            # 相対URLを取得
            href = await link.get_attribute("href")
            # 絶対URLに変換
            href_full = parse.urljoin(page.url, href)
            links.append((curr, href_full))
            print(f"[INFO] {curr} のリンクを取得: {href}")
        else:
            print(f"[WARNING] {curr} のリンクが見つかりません")
    return links

async def get_kawase_info(page, links):
    """為替レート情報を取得"""  # --- (※10)
    kawase_data = []
    for curr, url in links:
        # 各通貨情報ページへナビゲート
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        print(f"[INFO] {curr} のページを取得: {url}")
        await asyncio.sleep(2)  # サーバー負荷軽減のために少し待つ --- (※11)
        # レート情報(#f_rate)を抽出 --- (※12)
        f_rate = await page.query_selector("#f_rate")
        if f_rate:
            rate_text = await f_rate.input_value()
            print(f"[INFO] {curr} の為替レート: {rate_text.strip()}")
            kawase_data.append([curr, rate_text.strip()])
        else:
            print(f"[WARNING] {curr} の為替レートが見つかりません")
    return kawase_data

async def save_to_csv(kawase_data):
    """取得した為替レート情報をCSVファイルに保存"""  # --- (※13)    
    # Excelで読めるようにShift_JISで為替レートCSVを保存
    with open(CSV_FILE, "w", newline="", encoding="shift_jis") as f:
        writer = csv.writer(f)
        writer.writerow(["通貨", "為替レート"])
        writer.writerows(kawase_data)
    print(f"[INFO] データを保存しました: {CSV_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
