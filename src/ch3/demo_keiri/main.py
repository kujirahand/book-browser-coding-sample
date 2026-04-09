#!/usr/bin/env python3
"""メイン処理 - 経理サイトから売り上げデータを取得してCSVファイルに保存する"""
import os
import traceback
from playwright.sync_api import sync_playwright
from scraper import login, get_branches, get_sales_data
from storage import save_to_csv

def main():
    """メイン処理""" # --- (※1)
    with sync_playwright() as p:
        # ブラウザを起動
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        try:
            # ログイン処理 --- (※2)
            login(page)
            # 支店一覧を取得 --- (※3)
            branches = get_branches(page)
            print(f"✓ {len(branches)}の支店が見つかりました")
            # 各支店の売り上げデータを取得 --- (※4)
            for branch_id, branch_name in branches:
                csv_filename = f"branch_{branch_id}.csv"
                # 既にファイルが存在する場合はスキップ
                if os.path.exists(csv_filename):
                    print(f"\n{csv_filename} は既に存在するのでスキップします")
                    continue
                # HTMLから売り上げデータを抽出 --- (※5)
                print(f"\n支店ID {branch_id} ({branch_name})のデータを取得中...")
                sales_data = get_sales_data(page, branch_id)
                # CSVファイルに保存 --- (※6)
                save_to_csv(sales_data, csv_filename)
                print(f"{csv_filename}: {len(sales_data)}件のデータを保存しました")
            print("\n全ての支店のデータ取得が完了しました")
        except Exception as e:
            # エラー処理 --- (※7)
            print(f"エラーが発生しました: {e}")
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    main()
