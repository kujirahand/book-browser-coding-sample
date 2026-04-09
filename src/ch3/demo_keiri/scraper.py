"""Playwright を使用したスクレイピング処理"""
import time
from config import *
from parser import extract_sales_from_page

def login(page):
    """ログインページにアクセスしてログインする"""
    # ログインページにアクセス --- (※1)
    print(f"ログインページにアクセス: {LOGIN_URL}")
    page.goto(LOGIN_URL)
    page.wait_for_load_state("networkidle")
    # JavaScriptが実行されるのを待つ
    print("JavaScriptの実行を待機中...")
    time.sleep(2)
    # ログインフォームに入力 --- (※2)
    print("ログイン情報を入力...")
    try:
        # ユーザーID入力欄を探して入力
        username_found = False
        for sel in USERNAME_SELECTORS:
            if page.query_selector(sel):
                page.fill(sel, USER_ID)
                username_found = True
                break
        if not username_found:
            raise ValueError("ユーザーID入力欄が見つかりません")
        # パスワード入力欄を探して入力
        password_found = False
        for sel in PASSWORD_SELECTORS:
            if page.query_selector(sel):
                page.fill(sel, PASSWORD)
                password_found = True
                break
        if not password_found:
            raise ValueError("パスワード入力欄が見つかりません")
        # ログインボタンをクリック
        submit_button_found = False
        for sel in SUBMIT_SELECTORS:
            btn = page.query_selector(sel)
            if btn:
                # クリック可能かチェック
                if btn.is_visible():
                    page.click(sel, timeout=5000)
                    submit_button_found = True
                    break
        if not submit_button_found:
            raise ValueError("ログインボタンが見つかりません")
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        print("✓ ログイン成功")
    except Exception as e:
        print(f"ログイン処理でエラー: {e}")
        raise

def get_branches(page):
    """支店一覧を取得"""  # --- (※3)
    branches = []
    # JavaScriptの実行を待つ
    time.sleep(2)
    # 支店一覧のテーブルから支店IDと支店名を取得 --- (※4)
    rows = page.query_selector_all('table tr')
    for row in rows[1:]:  # ヘッダー行をスキップ
        cells = row.query_selector_all('td')
        if len(cells) >= 2:
            # 支店IDのリンクを取得
            link = cells[0].query_selector('a')
            if link:
                branch_id = link.inner_text().strip()
                branch_name = cells[1].inner_text().strip()
                branches.append((branch_id, branch_name))
    return branches

def get_sales_data(page, branch_id):
    """指定した支店の全ての売り上げデータを取得"""  # --- (※5)
    all_sales = []
    page_num = 1
    # 支店IDのリンクをクリック
    page.click(f'a:has-text("{branch_id}")')
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        page.wait_for_load_state("load", timeout=5000)
    time.sleep(0.5)
    while page_num <= 10:  # 最大 10 ページまで取得
        # 現在のページのデータを取得 --- (※6)
        sales = extract_sales_from_page(page)
        all_sales.extend(sales)
        print(f"  ページ {page_num} を処理中...")
        # 次のページがあるかチェック ---- (※7)
        try:
            # "次へ" や ">" などのリンクを探す
            next_link = page.query_selector(
                'a:has-text("次"), a:has-text(">"), a:has-text("Next")'
            )
            if next_link and page_num < 10:  # 10ページ以上なら次ページをスキップ
                next_link.click()
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    page.wait_for_load_state("load", timeout=5000)
                time.sleep(3) # ページ遷移後のJavaScriptの実行を待つ
                page_num += 1
            else:
                break
        except Exception:
            break
    # 支店一覧に戻る --- (※8)
    try:
        page.click('a:has-text("戻る"), a:has-text("一覧")')
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            page.wait_for_load_state("load", timeout=5000)
    except Exception:
        # 戻るリンクがない場合は、支店一覧ページに直接遷移
        try:
            page.goto(page.url.split('?')[0])
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
    return all_sales
