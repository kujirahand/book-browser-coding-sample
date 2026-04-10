# Chrome拡張 - 掲示板の書き込みに対して、自動的に返信内容を作成してテキストボックスに挿入するツール

LM Studioと通信して、Webページのテキストボックスに自動的にLLMの応答を挿入するChrome拡張機能です。

## 機能

- 🤖 LM Studioのローカルモデルと通信
- 📝 Webページのテキストボックスに自動挿入
- 🎯 掲示板の書き込み `div.item` 要素を自動検出して入力として使用
- 💡 掲示板の書き込みがない場合は、適当に便利なTipsを生成

## インストール方法

### 1. LM Studioのセットアップ

1. [LM Studio](https://lmstudio.ai/)をダウンロードしてインストール
2. モデルをダウンロード（推奨: Llama 2, Mistral, Phi-2など）
3. LM Studioを起動し、「Local Server」タブを開く
4. サーバーを起動（デフォルト: http://localhost:1234）

### 2. Chrome拡張機能のインストール

1. Chromeで `chrome://extensions/` を開く
2. 右上の「デベロッパーモード」を有効にする
3. 「パッケージ化されていない拡張機能を読み込む」をクリック
4. このフォルダを選択

## 使い方

1. **LM Studioを起動**
   - モデルをロードしてローカルサーバーを起動します

2. **Webページを開く**
   - 任意のWebページを開きます

3. **LLM挿入ボタンをクリック**
   - ページ右下に表示される「🤖 LLM挿入」ボタンをクリック

4. **動作**
   - ページに `div.item` 要素がある場合：
     - 全ての `div.item` からテキストを抽出
     - LM Studioに送信して応答を生成
     - テキストボックスに挿入
   
   - ページに `div.item` 要素がない場合：
     - Chromeの便利なTipsを生成
     - テキストボックスに挿入

## ファイル構成

```
src/ch2/local_llm_bbs_ext/
├── manifest.json       # 拡張機能の設定ファイル
├── background.js       # LM Studioとの通信を担当
├── content.js          # Webページに注入されるスクリプト
├── popup.html          # 拡張機能のポップアップUI
├── popup.js            # UIのスクリプト
└── style.css           # UIのスタイルシート
```

## 技術仕様

### LM Studio API

- エンドポイント: `http://localhost:1234/v1/chat/completions`
- 互換性: OpenAI API互換
- リクエスト形式: JSON (POST)

### 対応テキスト入力要素

- `<textarea>`
- `<input type="text">`
- `<input>` (type未指定)
- `[contenteditable="true"]`

## カスタマイズ

### LM Studioのポート変更

[background.js](background.js#L4) の `LM_STUDIO_URL` を編集：

```javascript
const LM_STUDIO_URL = 'http://localhost:YOUR_PORT/v1/chat/completions';
```

### プロンプトのカスタマイズ

[content.js](content.js#L56-L67) の `prompt` 変数を編集：

```javascript
if (items.length > 0) {
  prompt = `カスタムプロンプト: ${itemTexts}`;
} else {
  prompt = 'カスタムデフォルトプロンプト';
}
```

### ボタンのスタイル変更

[content.js](content.js#L12-L27) の `button.style.cssText` を編集してください。

## トラブルシューティング

### LM Studioに接続できない

1. LM Studioが起動しているか確認
2. ローカルサーバーが有効になっているか確認
3. ポート番号が正しいか確認（デフォルト: 1234）

### テキストボックスに挿入されない

1. テキスト入力可能な要素があるか確認
2. ブラウザのコンソールでエラーを確認
3. 拡張機能を再読み込み

### div.itemが検出されない

- ページのHTMLソースで `<div class="item">` が存在するか確認
- セレクタを変更する場合は [content.js](content.js#L47) を編集
