# 高度なAPI型の広告ブロッカーを作ってみよう

Chrome拡張がネットワーク通信をブロックするためのDNR(Declarative Net Request)という機能を利用して、広告をブロックすることにしましょう。

これから作成するAPI型の広告ブロッカーは、次のようなファイル構成のプロジェクトにします。serverフォルダ以下にPythonのAPIサーバーのプログラムを入れます。

```
src/ch5/ad-blocker-dynamic/
├── manifest.json  --- ブラウザ拡張の設定ファイル
├── background.js  --- ブラウザ拡張のバックグラウンドスクリプト
├── popup.html  --- ブラウザ拡張のポップアップ画面のHTML
├── popup.js  --- ブラウザ拡張のポップアップ画面のJavaScript
├── popup.css  --- ブラウザ拡張のポップアップ画面のCSS
└── server/  --- APIサーバーのフォルダ
    ├── main.py --- APIサーバーのメインプログラム
    ├── requirements.txt  --- APIサーバーの依存ライブラリ一覧
    └── rules.json  --- ブロックルールの保存ファイル
 ```
 
## インストール - 依存ライブラリ
 
```sh
pip install fastapi uvicorn
```

## インストール - ブラウザ拡張

作成した拡張をChromeに登録しましょう。Chromeのアドレスバーに「chrome://extensions/」を入力し、「パッケージ化されていない拡張機能を読み込む」をクリックして、作成したプロジェクトのフォルダを選択します。これで、ブラウザに拡張機能がインストールされます。
 
## 実行

```sh
python server/main.py
```
 
 
 