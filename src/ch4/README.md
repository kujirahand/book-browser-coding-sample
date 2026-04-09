# 第4章のプログラム概要

この章では、Web技術を利用してデスクトップアプリを作る方法を学びます。pywebview、Electron、Tauri、Wailsを使い、それぞれの最小例と実用サンプルを収録しています。

## 含まれるプログラム

- `pywebview_simple.py`: pywebviewでウィンドウを表示する最小サンプルです。
- `pywebview_flask.py`: Flaskとpywebviewを組み合わせて画面を表示する例です。
- `pywebview_dice_js.py`: JavaScriptとPythonのやり取りを含むpywebviewの例です。
- `pywebview-notepad/`: pywebviewベースの簡易メモ帳アプリです。
- `electron-test-app/`: Electronアプリの最小構成例です。
- `electron-proverb-app/`: 格言を表示するElectronアプリです。
- `tauri-hello/`: Tauriの基本構成を確認するための最小プロジェクトです。
- `tauri-file-reader/`: TauriとRustでローカルファイルを読み込むアプリです。
- `wails-hello/`: Wailsの起動方法と基本構成を確認する最小プロジェクトです。
- `wails-notepad/`: WailsとGoで作るテキストエディタです。

## 学べること

- Web UIをデスクトップ化する基本パターン
- Python、Node.js、Rust、Goを使った連携方法
- フロントエンドとネイティブ処理のつなぎ方
- フレームワークごとの開発体験の違い

## 実行例

Pythonスクリプトは次のように実行します。

```bash
cd src/ch4
python pywebview_simple.py
```

Electronプロジェクトは各フォルダで依存関係をインストールして起動します。

```bash
cd src/ch4/electron-proverb-app
npm install
npm start
```

Tauriは各プロジェクトフォルダで `npm run tauri dev`、Wailsは `wails dev` を実行して確認します。
