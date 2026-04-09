# Tauriで画像ダウンローダーを作ろう

URLを指定すると、ページ内にある画像を一気にダウンロードするプログラムを作ってみましょう。

## 実行方法

```sh
npm install
npm run tauri dev
```

### Rustのプログラムの解説

本書でも詳しくプログラムの解説を行っていますが、Rustに関する説明は、ページ数が足りなかったので、ここでフォローしています。

ChatGPTに次のようなプロンプトを与えて説明させました。

```md
次のRustのコードは、Tauriのコードです。
JavaScript初心者でも分かるように、プログラムを解説してください。
特に、Rustの文法について、JavaScriptと対比して詳しく説明してください。
---
<ここにRustのプログラム>
```

- [src-tauri/src/lib.rs](src-tauri/src/lib.rs)の[解説はこちら](lib.md)
- [src-tauri/src/html_query.rs](src-tauri/src/html_query.rs)の[解説はこちら](html_query.md)
- [src-tauri/src/downloader.rs](src-tauri/src/downloader.rs)の[解説はこちら](downloader.md)
