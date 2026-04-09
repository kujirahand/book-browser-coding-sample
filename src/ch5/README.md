# 第5章のプログラム概要

この章では、ブラウザ拡張とデスクトップアプリを組み合わせた、より実践的なアプリ開発を扱います。広告ブロック、画像生成、可視化、ダウンロード支援など、応用寄りのサンプルが中心です。

## 含まれるプログラム

- `ad-blocker-css/`: CSSベースで広告要素を非表示にするシンプルな広告ブロッカー拡張です。
- `ad-blocker-dynamic/`: FastAPIとDNRを組み合わせ、ルールを動的に扱う高度な広告ブロッカーです。
- `fractal-image-tool/`: WailsとGoでマンデルブロ集合の画像を生成するアプリです。
- `tauri-visualizer/`: TauriとChart.jsでデータをグラフ表示する可視化アプリです。
- `tauri-image-downloader/`: TauriとRustでWeb上の画像を収集し保存するアプリです。

## 学べること

- 拡張機能を使ったページ制御
- APIサーバーと拡張機能の連携
- GoやRustを使ったデスクトップアプリ化
- 画像処理やデータ可視化の応用実装

## 実行例

拡張機能は第2章と同様に、Chromeの拡張機能管理画面から読み込みます。

`ad-blocker-dynamic` のサーバー側は次のように起動します。

```bash
cd src/ch5/ad-blocker-dynamic
pip install fastapi uvicorn
python server/main.py
```

WailsやTauriのアプリは、各プロジェクトフォルダで依存関係を入れたうえで `wails dev` または `npm run tauri dev` を実行します。
