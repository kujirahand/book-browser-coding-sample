#!/usr/bin/env python3
"""
経理サイトから売り上げデータを取得してCSVファイルに保存するスクリプト
"""
import csv
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ログイン情報 --- (※1)
LOGIN_URL = "https://api.aoikujira.com/demo_keiri/login.php"
USER_ID = "admin"
PASSWORD = "pOuIohVNS4aDOY8i"

def login(page):
    """ログインページにアクセスしてログインする"""
    # ログインページにアクセス
    print(f"ログインページにアクセス: {LOGIN_URL}")
    page.goto(LOGIN_URL)
    page.wait_for_load_state("networkidle")
    
    # JavaScriptが実行されるのを待つ
    print("JavaScriptの実行を待機中...")
    time.sleep(2)
    
    # ログインフォームに入力
    print("ログイン情報を入力...")
    try:
        # ユーザーID入力欄を探して入力
        username_selectors = [
            '#username',
            '[name="username"]',
            'input[type="text"]']
        username_found = False
        for sel in username_selectors:
            if page.query_selector(sel):
                page.fill(sel, USER_ID)
                username_found = True
                break
        if not username_found:
            raise ValueError("ユーザーID入力欄が見つかりません")
        
        # パスワード入力欄を探して入力
        password_selectors = [
            '#password',
            '[name="password"]',
            'input[type="password"]']
        password_found = False
        for sel in password_selectors:
            if page.query_selector(sel):
                page.fill(sel, PASSWORD)
                password_found = True
                break
        if not password_found:
            raise ValueError("パスワード入力欄が見つかりません")
        
        # ログインボタンをクリック
        submit_selectors = ['button[type="submit"]', 'button', 'input[type="submit"]']
        submit_button_found = False
        for sel in submit_selectors:
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
        time.sleep(1)
        
        print("✓ ログイン成功")
    except Exception as e:
        print(f"ログイン処理でエラー: {e}")
        raise

def main():
    with sync_playwright() as p:
        # ブラウザを起動
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # ログイン処理
            login(page)
            
            # 支店一覧を取得
            branches = get_branches(page)
            print(f"✓ {len(branches)}の支店が見つかりました")
            
            # 各支店の売り上げデータを取得
            for branch_id, branch_name in branches:
                csv_filename = f"branch_{branch_id}.csv"
                
                # 既にファイルが存在する場合はスキップ
                import os
                if os.path.exists(csv_filename):
                    print(f"\n{csv_filename} は既に存在するのでスキップします")
                    continue
                
                print(f"\n支店ID {branch_id} ({branch_name}) のデータを取得中...")
                sales_data = get_sales_data(page, branch_id)
                
                # CSVファイルに保存
                save_to_csv(sales_data, csv_filename)
                print(f"{csv_filename} に {len(sales_data)} 件のデータを保存しました")
            
            print("\n✅ 全ての支店のデータ取得が完了しました")
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

def get_branches(page):
    """支店一覧を取得"""
    branches = []
    
    # JavaScriptの実行を待つ
    time.sleep(2)
    
    # 支店一覧のテーブルから支店IDと支店名を取得
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
    """指定した支店の全ての売り上げデータを取得"""
    all_sales = []
    page_num = 1
    
    # 支店IDのリンクをクリック
    page.click(f'a:has-text("{branch_id}")')
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except:
        page.wait_for_load_state("load", timeout=5000)
    time.sleep(0.5)
    
    while True:
        # 現在のページのデータを取得
        sales = extract_sales_from_page(page)
        all_sales.extend(sales)
        
        # 次のページがあるかチェック
        try:
            # "次へ" や ">" などのリンクを探す
            next_link = page.query_selector('a:has-text("次"), a:has-text(">"), a:has-text("Next")')
            
            if next_link:
                next_link.click()
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    page.wait_for_load_state("load", timeout=5000)
                time.sleep(0.5)
                page_num += 1
            else:
                break
        except:
            break
    
    # 支店一覧に戻る
    try:
        page.click('a:has-text("戻る"), a:has-text("一覧")')
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            page.wait_for_load_state("load", timeout=5000)
    except:
        # 戻るリンクがない場合は、支店一覧ページに直接遷移
        try:
            page.goto(page.url.split('?')[0])
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
    
    return all_sales

def extract_sales_from_page(page):
    """現在のページから売り上げデータを抽出"""
    sales = []
    
    # テーブルから行を取得
    rows = page.query_selector_all('table tr')
    
    for row in rows[1:]:  # ヘッダー行をスキップ
        cells = row.query_selector_all('td')
        if len(cells) >= 8:
            sale = {
                '取引ID': cells[0].inner_text().strip(),
                '日時': cells[1].inner_text().strip(),
                '商品ID': cells[2].inner_text().strip(),
                '商品名': cells[3].inner_text().strip(),
                '単価': cells[4].inner_text().strip(),
                '数量': cells[5].inner_text().strip(),
                '小計': cells[6].inner_text().strip(),
                '支払い方法': cells[7].inner_text().strip(),
            }
            sales.append(sale)
    
    return sales

def save_to_csv(sales_data, filename):
    """売り上げデータをCSVファイルに保存"""
    if not sales_data:
        print(f"  警告: {filename} に保存するデータがありません")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['取引ID', '日時', '商品ID', '商品名', '単価', '数量', '小計', '支払い方法']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for sale in sales_data:
            writer.writerow(sale)

if __name__ == "__main__":
    main()
