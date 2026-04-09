# 第3章のプログラム概要

この章では、ブラウザ自動操作とスクレイピングの基本から実務寄りの取得処理までを扱います。静的HTML解析、Selenium、Playwright、ログイン後のデータ取得といった段階的な題材で構成されています。

## 含まれるプログラム

- [scraping_test.py](scraping_test.py): `requests` とBeautifulSoupを使ってページのタイトルや見出しを取得する、静的スクレイピングの基本例です。
- [selenium_test.py](selenium_test.py): Seleniumを使ってブラウザを自動操作するための導入サンプルです。
- [playwright_test.py](playwright_test.py): Playwrightでページを開き、タイトルや要素テキストを取得する基本例です。
- [login_download.py](login_download.py): ログイン後に画面遷移しながらデータを取得する自動処理の例です。
- [playwright_kawase.py](playwright_kawase.py): Playwrightで為替データなどを扱う取得処理のサンプルです。
- [sakusi_get_list.py](sakusi_get_list.py): 特定サイトから作品一覧を収集するPlaywrightスクリプトです。
- [sakusi_get_list_to_csv.py](sakusi_get_list_to_csv.py): 取得した一覧をCSVへ保存する版です。
- [demo_keiri](demo_keiri/): 複数画面の巡回、抽出、保存をまとめた実務寄りのサンプルプロジェクトです。

## 学べること

- 静的スクレイピングと動的操作の違い
- SeleniumとPlaywrightの基本操作
- ログインが必要なページの扱い方
- 取得結果のCSV保存
- 実務的な自動処理の構成分割

## 実行例

単体スクリプトは、次のように実行します。

```bash
cd src/ch3
python scraping_test.py
python playwright_test.py
```

PlaywrightやSeleniumを使うスクリプトは、事前に必要ライブラリやブラウザドライバのセットアップが必要です。`demo_keiri` については `src/ch3/demo_keiri/AGENTS.md` も参照してください。
