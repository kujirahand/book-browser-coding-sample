# TauriとChart.jsでデータ可視化アプリを作ろう

支店の売上グラフを表示するデスクトップアプリを作ります。書籍の3章で、Webアプリから支店の売り上げ情報をCSVに保存するプログラムを作ってみました。今回は、そのCSVファイルを読み込んで、支店の売り上げ情報をグラフ化して表示するデスクトップアプリをTauriで作成してみましょう。

## インストールの方法について

```sh
cd tauri-visualizer
# Tauriと依存ライブラリをインストール
npm install
# Tauriで実行
npm run tauri dev
```

## Rustについての説明

CSVファイルの列挙や読み取りなどの処理は、バックエンドのRust側で実装しました。

以下のプロンプトを使って、Rustの解説を行わせてみます。

```md
以下は、Tauriのバックエンド側のライブラリです。
JavaScript初心者にもわかりやすく、プログラムの動作を解説してください。
特に、Rustの文法の解説を多く入れてください。

<プログラム>
```

Rustに関する解説は次の通りです。

- [src-tauri/src/lib.rs](src-tauri/src/lib.rs)の[解説はこちら](lib.md)
- [src-tauri/src/csv_processing.rs](src-tauri/src/csv_processing.rs)の[解説はこちら](csv_processing.md)

