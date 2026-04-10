# Tauriでファイルを読み出すプログラムを作ろう

Tauriで、デスクトップに配置したテキストファイル「sample.txt」を読み出して、表示するツールを作ってみましょう。

このサンプルでは、フロントエンドのJavaScriptからRust側の関数を呼び出し、ネイティブ側でファイルを読み込んで、その結果を画面のテキストエリアに表示します。

## このサンプルで分かること

- TauriでフロントエンドとRustバックエンドを連携する方法
- JavaScriptからinvokeでRustのコマンドを呼び出す流れ
- Rust側でデスクトップフォルダのパスを取得し、ファイルを読む方法
- 読み込んだ文字列をフロントエンドの画面に反映する方法

---------------

## (参考) Rustに初めて触れる方へ

Rustのコードが難しいと感じる場合は、生成AIの力を借りて、Rustのコードを解説してもらうと理解が深まります。次のようなプロンプトが役立ちます。

```md
Rust初心者です。
以下は、Tauriでライブラリを記述するコードです。
分かりやすく、JavaScriptで書くとどうなるのか、部分ごとに教えてください。
--------------
<Rustのコード>
```

実際に上記のプロンプトを生成AI(ChatGPT)に与えて、Rustのコードについて解説させたものを以下に配置しました。本書の解説と併せて参考にしてください。Rustの文法についてJavaScriptと対比させて解説しているので、理解が深まります。

- [src-tauri/src/lib.rs](src-tauri/src/lib.rs) の解説を [lib.md](lib.md) にまとめています。
- [src-tauri/src/main.rs](src-tauri/src/main.rs) の解説を [main.md](main.md) にまとめています。

---------------

## ファイルを読み出すプログラムを実行する事前準備

このプログラムは、デスクトップ上にある sample.txt を読み込みます。
実行前に、デスクトップに sample.txt を配置してください。

リポジトリ内にも [sample.txt](sample.txt) を置いてありますが、これは内容確認用です。実際にアプリが参照するのはデスクトップ上の sample.txt です。

## 実行方法

```sh
cd tauri-file-reader
npm install
npm run tauri dev
```

起動すると、Rust側で sample.txt を読み込み、その内容が画面に表示されます。

## 主なファイル構成

- [src/main.js](src/main.js) - フロントエンドの画面生成と Rust 呼び出し
- [src-tauri/src/lib.rs](src-tauri/src/lib.rs) - ファイル読み込みを行う Rust のコマンド定義
- [src/index.html](src/index.html) - アプリのベースHTML
- [src/styles.css](src/styles.css) - 画面スタイル
- [src-tauri/Cargo.toml](src-tauri/Cargo.toml) - Rust側の依存設定
- [package.json](package.json) - Tauri CLI 実行設定
- [sample.txt](sample.txt) - 読み込み対象のサンプルテキスト

## 動作の流れ

1. アプリ起動時に [src/main.js](src/main.js) が実行されます。
2. JavaScript側で画面のHTMLを組み立て、テキストエリアを表示します。
3. その後、invoke("read_file", { filename: "sample.txt" }) を使って Rust の read_file 関数を呼び出します。
4. [src-tauri/src/lib.rs](src-tauri/src/lib.rs) では、デスクトップフォルダを取得し、sample.txt を読み込みます。
5. 読み込んだ文字列が JavaScript 側に返され、テキストエリアに表示されます。

## 実装のポイント

### フロントエンド側

[src/main.js](src/main.js) では、DOMContentLoaded のタイミングで画面を初期化し、Tauri の invoke API を使って Rust 側の read_file を呼び出しています。

- 画面のHTMLをJavaScriptで直接生成している
- invoke を使ってバックエンド関数を非同期で呼び出している
- 取得したテキストを textarea に設定して表示している

### Rust側

[src-tauri/src/lib.rs](src-tauri/src/lib.rs) では、#[tauri::command] を使って、フロントエンドから呼べる read_file 関数を定義しています。

- app.path().desktop_dir() でデスクトップフォルダを取得する
- join でファイル名を結合して完全なパスを作る
- std::fs::read_to_string でファイル内容を文字列として読む
- 読み込みに失敗した場合は、エラーメッセージを文字列で返す

## このサンプルを発展させるには

この例は、Tauriでネイティブ機能を呼び出す最小構成のひとつです。ここから次のような機能を加えると、より実践的になります。

- 任意のファイル名を入力して読み込めるようにする
- ファイル選択ダイアログを表示して読み込む
- 読み込んだ内容を編集して保存できるようにする
- 文字コードやエラー表示を改善する
