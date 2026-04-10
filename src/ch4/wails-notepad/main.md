# main.goをJavaScript風に解説したもの

- [main.go](main.go)の内容を、JavaScriptで書くとどうなるか、という観点で解説します。これは、アプリ全体の起動を担当するコードです。

役割としては、JavaScript でいうと **アプリの起動設定を書くブートストラップ** に近いです。

まず、JavaScript っぽく表すと、イメージはこうなります。

```javascript
// ※これは説明用の擬似コードです
// 実際にこのままWailsで動くJavaScriptではありません

import { runApp } from "wails";
import { NewApp } from "./app.js";
import assets from "./frontend/dist"; // イメージ

function main() {
  const app = NewApp();

  const err = runApp({
    title: "wails-notepad",
    width: 1024,
    height: 768,
    assetServer: {
      assets: assets,
    },
    backgroundColour: { r: 27, g: 38, b: 54, a: 1 },
    onStartup: app.startup.bind(app),
    bind: [app],
  });

  if (err) {
    console.error("Error:", err.message);
  }
}

main();
```

ただし、これも前回と同じで、**「JavaScriptで同じ役割を書くとこう見える」** という説明用です。
Wails の実際の JavaScript API をそのまま表したものではありません。

---

## このコード全体が何をしているか

この `main.go` は、ひとことで言うと次の役目です。

* フロントエンドの `frontend/dist` をアプリに組み込む
* `App` のインスタンスを作る
* ウィンドウサイズやタイトルを設定する
* 起動時に `startup()` を呼ぶよう設定する
* `App` のメソッドをフロントエンドから呼べるようにする
* 最後にアプリを起動する

JavaScript でいえば、**アプリ初期化 + ウィンドウ設定 + バックエンド公開**です。

---

# 一行ずつ対比して説明

---

## 1. パッケージ宣言

### Go

```go
package main
```

### JavaScript

```javascript
// JavaScriptには package main に相当するものはない
```

### 説明

Go では、このファイルが `main` パッケージに属していて、
さらに `main()` 関数を持つことで**実行可能プログラム**になります。

JavaScript には `package main` はありません。
単に「エントリーファイル」として扱います。

---

## 2. embed パッケージの読み込み

### Go

```go
import (
	"embed"
```

### JavaScript

```javascript
// JSには embed にそのまま対応する標準機能はない
```

### 説明

Go の `embed` は、**ファイルを実行ファイルの中に埋め込む**ための機能です。

JavaScript だと近い感覚は、

* bundler がファイルをまとめる
* 静的ファイルをビルド成果物に含める

ですが、Go の `embed` はもっと直接的で、
**バイナリの中にファイルを持ち込む**仕組みです。

---

## 3. Wails 本体の import

### Go

```go
	"github.com/wailsapp/wails/v2"
```

### JavaScript

```javascript
import { runApp } from "wails";
```

### 説明

Go 側で Wails 本体を読み込んでいます。
JavaScript で言えば、ライブラリ本体を import するイメージです。

このコードでは後で `wails.Run(...)` を呼ぶために必要です。

---

## 4. options パッケージの import

### Go

```go
	"github.com/wailsapp/wails/v2/pkg/options"
```

### JavaScript

```javascript
// オプション用の型や設定オブジェクトを使うイメージ
```

### 説明

`options` は、Wails アプリの設定を書くためのパッケージです。

JavaScript では型をあまり意識しないので、
単に `runApp({ ... })` の設定オブジェクトを書く感じになります。

---

## 5. assetserver パッケージの import

### Go

```go
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
)
```

### JavaScript

```javascript
// assetServer 設定を使うための import に近い
```

### 説明

`assetserver` は、フロントエンドのファイルを配る仕組みの設定です。
ここでは `frontend/dist` を Wails に渡すために使います。

---

## 6. go:embed ディレクティブ

### Go

```go
//go:embed all:frontend/dist
```

### JavaScript

```javascript
// frontend/dist をアプリに含める、という宣言に近い
```

### 説明

これは Go の特別なコメントです。
`frontend/dist` 以下のファイルを、**実行ファイルに埋め込め**という意味です。

JavaScript にはこの書き方はありません。
近い考え方は、Webpack や Vite が `dist` をまとめる感じです。

ただし Go の場合は、**実行ファイルの中にそのまま持ち込む**のが特徴です。

---

## 7. 埋め込まれたファイル群を変数に入れる

### Go

```go
var assets embed.FS
```

### JavaScript

```javascript
const assets = /* 埋め込まれたフロントエンド資産 */;
```

### 説明

`embed.FS` は、埋め込まれたファイルを扱うための特別なファイルシステムです。

JavaScript でそのまま同じ型はありませんが、感覚としては

* 静的ファイル一式
* ビルド済みフロントエンド資産

を `assets` に持っている感じです。

---

## 8. main 関数の開始

### Go

```go
func main() {
```

### JavaScript

```javascript
function main() {
```

### 説明

Go のプログラムはここから始まります。
JavaScript でも普通の `main()` 関数に相当します。

---

## 9. コメント

### Go

```go
	// Create an instance of the app structure
```

### JavaScript

```javascript
  // App のインスタンスを作る
```

### 説明

これは単なるコメントです。

---

## 10. App インスタンスを作る

### Go

```go
	app := NewApp()
```

### JavaScript

```javascript
  const app = NewApp();
```

### 説明

ここは前回の `app.go` とつながっています。
`NewApp()` で `App` のインスタンスを作っています。

Go の `:=` は、**変数宣言と代入を同時に行う記法**です。
JavaScript の `const app = ...` にかなり近いです。

---

## 11. コメント

### Go

```go
	// Create application with options
```

### JavaScript

```javascript
  // オプションを指定してアプリを作る
```

### 説明

これもコメントです。

---

## 12. Wails アプリを起動する

### Go

```go
	err := wails.Run(&options.App{
```

### JavaScript

```javascript
  const err = runApp({
```

### 説明

ここがこのファイルの中心です。

Go では `wails.Run(...)` に設定を渡してアプリを起動します。
JavaScript でいえば、`runApp({...})` のように設定オブジェクトを渡して起動する感じです。

ポイントはこの `&options.App{ ... }` です。

* `options.App` は設定用の構造体
* `{ ... }` で中身を埋める
* `&` はそのポインタを渡す

JavaScript にはポインタがないので、単純にオブジェクトを渡す感覚です。

---

## 13. タイトル設定

### Go

```go
		Title:  "wails-notepad",
```

### JavaScript

```javascript
    title: "wails-notepad",
```

### 説明

ウィンドウタイトルを設定しています。

Go は構造体フィールド名なので `Title`、
JavaScript では普通 `title` と書くイメージです。

---

## 14. 幅

### Go

```go
		Width:  1024,
```

### JavaScript

```javascript
    width: 1024,
```

### 説明

アプリウィンドウの幅です。
これはそのまま対応します。

---

## 15. 高さ

### Go

```go
		Height: 768,
```

### JavaScript

```javascript
    height: 768,
```

### 説明

アプリウィンドウの高さです。
これもそのままです。

---

## 16. AssetServer 設定開始

### Go

```go
		AssetServer: &assetserver.Options{
```

### JavaScript

```javascript
    assetServer: {
```

### 説明

フロントエンド資産をどのように配るかの設定です。

Go では `assetserver.Options` 構造体を作って渡しています。
JavaScript なら単なるネストしたオブジェクトです。

---

## 17. 埋め込んだ assets を指定

### Go

```go
			Assets: assets,
```

### JavaScript

```javascript
      assets: assets,
```

### 説明

先ほど `//go:embed` で埋め込んだ `frontend/dist` を、
Wails のアセットサーバーに渡しています。

つまり、「このフロントエンド一式を表示に使ってね」という指定です。

---

## 18. AssetServer 設定終了

### Go

```go
		},
```

### JavaScript

```javascript
    },
```

### 説明

ネストした設定オブジェクトの終わりです。

---

## 19. 背景色設定

### Go

```go
		BackgroundColour: &options.RGBA{R: 27, G: 38, B: 54, A: 1},
```

### JavaScript

```javascript
    backgroundColour: { r: 27, g: 38, b: 54, a: 1 },
```

### 説明

ウィンドウ背景色です。

Go では `options.RGBA` 構造体を作っています。
JavaScript なら普通のオブジェクトです。

少しだけ気をつけると、Go のフィールド名は大文字です。

* `R`
* `G`
* `B`
* `A`

JavaScript なら小文字で書くことが多いです。

---

## 20. 起動時コールバック

### Go

```go
		OnStartup:        app.startup,
```

### JavaScript

```javascript
    onStartup: app.startup.bind(app),
```

### 説明

ここはとても大事です。

Wails が起動したときに、`app.startup` を呼びます。
前回の `app.go` で書いたこの部分です。

```go
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}
```

JavaScript でも似たことはできますが、
JS では `this` がずれないように `bind(app)` が必要になる場面があります。

なので説明用には `app.startup.bind(app)` と書くのが分かりやすいです。

---

## 21. フロントエンドへ公開するオブジェクト

### Go

```go
		Bind: []interface{}{
			app,
		},
```

### JavaScript

```javascript
    bind: [app],
```

### 説明

これも Wails で超重要です。

`Bind` に `app` を入れることで、
`App` の公開メソッドがフロントエンドから呼べるようになります。

つまり前回の `Save()` や `Load()` を、
フロントエンドの JavaScript / TypeScript から呼べるのはここのおかげです。

Go の

```go
[]interface{}{}
```

は、ざっくり言うと「何でも入れられる配列」です。
JavaScript の配列 `[]` にかなり近い感覚です。

---

## 22. wails.Run 呼び出し終了

### Go

```go
	})
```

### JavaScript

```javascript
  });
```

### 説明

設定オブジェクトを渡し終わって、`runApp()` を閉じています。

---

## 23. エラーチェック

### Go

```go
	if err != nil {
```

### JavaScript

```javascript
  if (err) {
```

### 説明

Go は `Run()` が返した `err` を明示的にチェックします。
JavaScript でも `if (err)` に相当しますが、実際には例外で扱うことも多いです。

---

## 24. エラー表示

### Go

```go
		println("Error:", err.Error())
```

### JavaScript

```javascript
    console.error("Error:", err.message);
```

### 説明

Go の `err.Error()` は、エラーを文字列に変換しています。
JavaScript では `err.message` が近いです。

`println()` は、JS の `console.error()` や `console.log()` に相当します。

---

## 25. if と main の終了

### Go

```go
	}
}
```

### JavaScript

```javascript
  }
}
```

### 説明

ここで `if` と `main()` が終わります。

---

# このコードの役割を JavaScript 的に言い換えると

かなりざっくり言うと、この `main.go` は JavaScript でいう次の役です。

* `frontend/dist` を読み込む
* `App` を1個作る
* ウィンドウ設定をする
* 起動時フックを登録する
* `App` をフロントエンドに公開する
* アプリを起動する

つまり、**設定ファイル兼エントリーポイント**です。

---

# 前回の `app.go` とのつながり

前回の `app.go` では、`Save()` と `Load()` を定義していました。
今回の `main.go` では、その `app` をこうして登録しています。

```go
Bind: []interface{}{
	app,
},
```

これにより、フロントエンド側からはだいたいこんな感じで呼べます。

```javascript
import { Save, Load } from "../wailsjs/go/main/App";

const filename = await Save("メモ内容");
const text = await Load();
```

つまり、

* `app.go` → 何ができるかを書く
* `main.go` → その機能をWailsに登録して起動する

という役割分担です。

---

# Go初心者向けの読み方のコツ

このコードで特に覚えると読みやすくなるのは次の5つです。

### 1. `:=`

```go
app := NewApp()
```

これは JavaScript の

```javascript
const app = NewApp();
```

みたいなものです。

---

### 2. `&`

```go
&options.App{ ... }
```

これは「その構造体のポインタを渡す」です。
JavaScript ではあまり気にしなくて大丈夫です。

---

### 3. 構造体初期化

```go
options.App{
    Title: "wails-notepad",
    Width: 1024,
}
```

これは JavaScript の

```javascript
{
  title: "wails-notepad",
  width: 1024
}
```

にかなり近いです。

---

### 4. `[]interface{}`

```go
[]interface{}{ app }
```

これは JavaScript の

```javascript
[app]
```

みたいなものです。

---

### 5. `err != nil`

```go
if err != nil {
```

これは JavaScript の

```javascript
if (err) {
```

に近いです。

