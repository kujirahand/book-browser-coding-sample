# Copy Title Extension - ページタイトルをコピーするブラウザ拡張

表示中のページのタイトルとURLを取得し、ワンクリックでクリップボードへコピーするブラウザ拡張です。

## ファイル構成

- [manifest.json](manifest.json) - 拡張の設定ファイル
- [popup.html](popup.html) - ポップアップUI
- [popup.js](popup.js) - タイトル取得とコピー処理のスクリプト

## インストール方法

### Chrome/Edge（開発者モード）

1. `chrome://extensions/` を開く
2. 右上の「開発者モード」をONにする
3. 「パッケージ化されていない拡張機能を読み込む」をクリックする
4. このフォルダを選択する

## 使い方

1. 任意のWebページを開く
2. ブラウザのツールバーにある拡張アイコンをクリックする
3. ポップアップに現在のページタイトルとURLが表示される
4. 「クリップボードにコピー」を押す
5. タイトルとURLが次の形式でコピーされる

```text
ページタイトル
[URL] https://example.com
```

## 実装のポイント

- `chrome.tabs.query()` でアクティブなタブの情報を取得します
- 取得したタイトルとURLをポップアップ内に表示します
- ボタンを押すと `navigator.clipboard.writeText()` でクリップボードへ書き込みます
- 必要な権限は `activeTab` と `clipboardWrite` です
