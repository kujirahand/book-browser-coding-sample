# Wailsを使ってフラクタル画像生成ツールを作ろう

Wailsを使ってフラクタル画像生成ツールを作ってみましょう。Go言語側では、マンデルブロ集合の計算を行い、生成された画像をPNG形式で保存できるようにします。フロントエンドでは、ユーザーが画像のサイズや色を選択できるようなインターフェースを作成します。

## インストール

```sh
# ライブラリ(go-colorful)をインストール
go get github.com/lucasb-eyer/go-colorful@latest
```

## Go言語のプログラムについて

本書でも、一通りGo言語のプログラムを解説していますが、プログラミングがある程度できる人向けの説明になっています。次のプロンプトを用いてChatGPTに解説させると、次のようになります。

```md
以下のGo言語のプログラムを、JavaScript初心者でも分かるように解説してください。特に、Go言語の文法について、詳しく解説してください。
-----
\`\`\`go
<プログラム>
\`\`\`
```

### src/ch5/fractal-image-tool/app.go

[app.go](app.go)をChatGPTに与えると、次のような解説がでます。

このコードは、**Wails で作るデスクトップアプリの Go 側**を担当しています。役割をひとことで言うと、

* **Go側** … マンデルブロ集合の画像を計算して PNG を作る
* **フロントエンド側** … ボタンや入力欄を表示して、Go側の関数を呼ぶ

という分担です。

JavaScript初心者向けに、まず全体像を説明して、そのあとに **Go言語の文法** をかなり丁寧に分解します。

---

# このプログラムがしていること

この Go プログラムは主に次の3つをしています。

1. **Wailsアプリの本体を定義する**
2. **保存ダイアログを表示する**
3. **マンデルブロ集合の画像を生成し、PNGとして返す／保存する**

---

# まずは全体像

このコードに出てくる主な関数は次の通りです。

* `NewApp()`
  アプリ本体を作る

* `startup(ctx)`
  起動時に呼ばれて、Wailsの情報を受け取る

* `OpenSaveDialog()`
  保存先を選ぶダイアログを開く

* `SaveB64Image(dataURL, filename)`
  Base64形式の画像文字列を実際のPNGファイルとして保存する

* `GenImage(cx, cy, zoom, maxIter)`
  マンデルブロ画像を作って、Base64付きの文字列として返す

* `genImage(...)`
  画像を1ピクセルずつ計算して作る

* `pxToComplex(...)`
  画面上のピクセル座標を複素数平面の座標に変換する

* `iterMandelbrot(...)`
  その点がマンデルブロ集合に属するかを繰り返し計算する

* `pixelColor(...)`
  計算結果から色を決める

---

# Goの文法の基本を最初に

JavaScript と比べながら、先に重要な文法だけ押さえます。

## 1. `package main`

```go
package main
```

これは「このファイルは `main` パッケージに属します」という意味です。

JavaScript にはほぼそのまま対応する書き方はありませんが、感覚としては、

* Node.js の1ファイル
* あるいはエントリーポイント用のモジュール

に近いです。

Goでは、コードは「パッケージ」という単位でまとめます。
`main` パッケージは、実行可能プログラムの入り口になる特別なパッケージです。

---

## 2. `import`

```go
import (
	"bytes"
	"context"
	"encoding/base64"
	"image"
	"image/color"
	"image/png"
	"math"
	"os"

	"github.com/lucasb-eyer/go-colorful"
	wails "github.com/wailsapp/wails/v2/pkg/runtime"
)
```

これはライブラリの読み込みです。

JavaScript だとこんな感じです。

```js
import fs from "fs";
import path from "path";
```

に近いですが、Goでは複数まとめて書けます。

特にこの行が大事です。

```go
wails "github.com/wailsapp/wails/v2/pkg/runtime"
```

これは **別名を付けて import** しています。
つまり、本来長い名前のパッケージを `wails` という短い名前で使えるようにしています。

JavaScriptならこういう感覚です。

```js
import * as wails from "some-long-package-name";
```

---

# 構造体とメソッド

Go初心者が最初につまずきやすいところです。

## 3. `type App struct`

```go
type App struct {
	ctx context.Context
}
```

これは **構造体** の定義です。

JavaScriptに完全に同じ仕組みはありませんが、感覚としてはクラスのインスタンスが持つプロパティに近いです。

JavaScript風に書くと、だいたいこういうイメージです。

```js
class App {
  constructor() {
    this.ctx = null;
  }
}
```

Goでは `class` はありません。
その代わりに、

* データを持つ箱 → `struct`
* その箱に対する関数 → メソッド

を組み合わせて使います。

この `App` は、Wailsアプリ全体を表す入れ物です。
中に `ctx` という値を1つ持っています。

---

## 4. `func NewApp() *App`

```go
func NewApp() *App {
	return &App{}
}
```

これは `App` を作る関数です。

JavaScriptで言えばこんな感じです。

```js
function NewApp() {
  return new App();
}
```

Goのポイントは2つです。

### `func`

関数を定義するときのキーワードです。

JavaScriptの

```js
function hello() {}
```

に相当します。

---

### `*App`

戻り値の型です。
`*App` は **App へのポインタ** を意味します。

初心者向けには、ひとまず

* `App` … 本体そのもの
* `*App` … その本体を指す参照っぽいもの

と考えて大丈夫です。

JavaScriptではオブジェクトは参照で扱われるので、感覚的にはかなり近いです。

---

### `&App{}`

これは **App構造体を新しく作って、そのアドレスを返す** 書き方です。

* `App{}` … 空の App を作る
* `&App{}` … その参照を返す

JavaScriptなら `new App()` の感覚に近いです。

---

## 5. メソッドの定義

```go
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}
```

これは `App` のメソッドです。

JavaScriptならこうです。

```js
class App {
  startup(ctx) {
    this.ctx = ctx;
  }
}
```

Go独特なのはここです。

```go
func (a *App) startup(...)
```

この `(a *App)` を **レシーバ** と呼びます。
「この関数は `App` に属している」という意味です。

JavaScriptの `this` を使うメソッド定義に近いです。

* `a` … JavaScriptでいう `this` のようなもの
* `*App` … App型のメソッドであることを示す

つまり、

```go
a.ctx = ctx
```

は JavaScript の

```js
this.ctx = ctx;
```

に相当します。

---

# ここからコードを順番に解説

---

## 1. Wailsアプリの構造体

```go
type App struct {
	ctx context.Context
}
```

この `ctx` は、Wailsが起動時に渡してくれるアプリの文脈情報です。
保存ダイアログなどを開くときに必要になります。

### 文法ポイント

* `type App struct { ... }`
  新しい構造体型を定義する
* `ctx context.Context`
  `ctx` という名前のフィールド。型は `context.Context`

JavaScriptだと型は書きませんが、Goでは **変数やフィールドに型を書く** のが基本です。

---

## 2. アプリを作る関数

```go
func NewApp() *App { // アプリの構造体を初期化
	return &App{}
}
```

これは「新しい App を作って返す」関数です。

### 文法ポイント

#### `func NewApp() *App`

* `func` … 関数定義
* `NewApp` … 関数名
* `()` … 引数なし
* `*App` … 戻り値の型

#### `return &App{}`

* `return` … 戻り値を返す
* `&App{}` … App構造体を新しく作って返す

---

## 3. 起動時の処理

```go
func (a *App) startup(ctx context.Context) { // 起動時に呼び出される関数
	a.ctx = ctx
}
```

Wailsがアプリ起動時に自動で呼ぶメソッドです。
ここで渡された `ctx` を保存しておきます。

あとで `OpenSaveDialog()` の中で、

```go
wails.SaveFileDialog(a.ctx, saveDialogOptions)
```

のように使います。

### JavaScript風イメージ

```js
startup(ctx) {
  this.ctx = ctx;
}
```

---

# 保存ダイアログを開く部分

## 4. `OpenSaveDialog`

```go
func (a *App) OpenSaveDialog() (string, error) {
```

ここで初心者に重要なのが、**Goの関数は戻り値を複数返せる** ことです。

これは JavaScript とかなり違います。

JavaScriptなら普通はこうです。

```js
function openSaveDialog() {
  return { filename, error };
}
```

でも Go ではこう書けます。

```go
func (...) (string, error)
```

つまり、

* 1つ目の戻り値: `string`
* 2つ目の戻り値: `error`

を返す関数です。

これは Go の超重要文法です。

---

## 5. 構造体リテラルでオプションを作る

```go
saveDialogOptions := wails.SaveDialogOptions{
	DefaultFilename: "mandelbrot.png",
	Filters: []wails.FileFilter{
		{DisplayName: "PNG画像", Pattern: "*.png"},
		{DisplayName: "全てのファイル", Pattern: "*.*"},
	},
}
```

ここは Go の文法がたくさん詰まっています。

---

### `:=` とは？

```go
saveDialogOptions := ...
```

`:=` は **短い変数宣言** です。

JavaScriptで言うとこんな感じです。

```js
const saveDialogOptions = ...
```

に近いです。

Goでは、

* `var x string = "abc"` のように書く方法
* `x := "abc"` のように短く書く方法

があります。

`:=` は「新しい変数を、その場で型推論して作る」という意味です。

---

### 構造体リテラル

```go
wails.SaveDialogOptions{
	DefaultFilename: "mandelbrot.png",
	Filters: ...
}
```

これは JavaScript のオブジェクトリテラルにかなり近いです。

JavaScriptならこうです。

```js
const saveDialogOptions = {
  DefaultFilename: "mandelbrot.png",
  Filters: [...]
};
```

Goでは、型名を前に付けて

```go
型名{
  フィールド名: 値,
}
```

と書きます。

---

### スライス `[]wails.FileFilter`

```go
Filters: []wails.FileFilter{
	{DisplayName: "PNG画像", Pattern: "*.png"},
	{DisplayName: "全てのファイル", Pattern: "*.*"},
},
```

これは **FileFilter型のスライス** です。

スライスは、JavaScriptでいえば配列に近いです。

```js
Filters: [
  { DisplayName: "PNG画像", Pattern: "*.png" },
  { DisplayName: "全てのファイル", Pattern: "*.*" }
]
```

Goでは `[]Type` で「Type の配列っぽいもの」を表します。

* `[]wails.FileFilter`
  `wails.FileFilter` の並び

---

## 6. ダイアログを開く

```go
filename, err := wails.SaveFileDialog(a.ctx, saveDialogOptions)
```

これも Go の重要ポイントです。

### 複数代入

Goでは、関数が複数の値を返したら、こう受け取れます。

```go
filename, err := ...
```

JavaScriptならこんな感じです。

```js
const [filename, err] = someFunction();
```

に少し似ていますが、Goではもっと普通に使います。

---

### `err`

Goではエラー処理を `throw` / `catch` よりも、**戻り値として受け取る** ことが多いです。

つまり、

* 成功したら `err == nil`
* 失敗したら `err != nil`

です。

---

## 7. エラーチェック

```go
if err != nil {
	return "", err
}
return filename, nil
```

Goではこれが定番です。

JavaScriptならこういう感覚です。

```js
if (err) {
  return ["", err];
}
return [filename, null];
```

### `nil`

`nil` は JavaScript の `null` に近いです。
ただし Go では、参照型やエラー型などに対して使います。

---

# Base64画像を保存する部分

## 8. `SaveB64Image`

```go
func (a *App) SaveB64Image(dataURL, filename string) error {
```

ここも文法的に大事です。

### 引数の書き方

Goでは、同じ型が続くとまとめて書けます。

```go
dataURL, filename string
```

これは省略しないとこういう意味です。

```go
dataURL string, filename string
```

JavaScriptならこうです。

```js
function saveB64Image(dataURL, filename) {}
```

Goでは型も書く必要があります。

---

### 戻り値が `error`

この関数は成功したら `nil` を返し、失敗したらエラーを返します。

JavaScriptなら例外を投げそうなところを、Goではよく `error` で返します。

---

## 9. 文字列プレフィックスの確認

```go
prefix := "data:image/png;base64,"
if !bytes.HasPrefix([]byte(dataURL), []byte(prefix)) {
	return os.ErrInvalid
}
```

この部分は、

* `dataURL` が本当に `data:image/png;base64,` で始まっているか
* そうでなければ無効なデータとしてエラーにする

という処理です。

### `!`

否定です。JavaScriptの `!` と同じです。

### `[]byte(dataURL)`

これは **文字列をバイト列に変換** しています。

JavaScriptだとあまり強く意識しませんが、Goでは

* `string`
* `[]byte`

は別物です。

---

## 10. 文字列の一部を切り出す

```go
base64Data := dataURL[len(prefix):]
```

これは **先頭のプレフィックス部分を除いた残り** を取り出しています。

JavaScriptならこうです。

```js
const base64Data = dataURL.slice(prefix.length);
```

Goでは `文字列[start:end]` で部分文字列を取り出します。

* `start` だけ書くと最後まで
* `:end` だけ書くと先頭から

です。

---

## 11. Base64デコード

```go
imgData, err := base64.StdEncoding.DecodeString(base64Data)
if err != nil {
	return err
}
```

Base64文字列をバイナリに戻しています。

### `return err`

この関数の戻り値は `error` だけなので、失敗したらそのまま返せます。

JavaScriptなら

```js
if (err) {
  throw err;
}
```

に近い感覚ですが、Goでは返すのが普通です。

---

## 12. ファイル保存

```go
return os.WriteFile(filename, imgData, 0644)
```

これは画像データをファイルに保存しています。

### `0644`

これはUnix系のファイル権限です。

初心者向けには、

* 所有者は読み書き可
* 他の人は読み取りのみ

くらいの理解で十分です。

JavaScriptではあまり見慣れませんが、Goでは OS に近い処理でよく出ます。

---

# PNG画像を生成する部分

## 13. `GenImage`

```go
func (a *App) GenImage(cx, cy, zoom float64, maxIter int) (string, error) {
```

ここも重要です。

### 引数の型まとめ

```go
cx, cy, zoom float64
```

これは

```go
cx float64, cy float64, zoom float64
```

の省略形です。

* `float64` … 小数
* `int` … 整数

JavaScriptは数字をほぼ全部 `number` で扱いますが、Goでは区別します。

---

## 14. 画像生成関数を呼ぶ

```go
img := genImage(600, 600, cx, cy, zoom, maxIter)
```

JavaScriptで言えば普通の関数呼び出しです。

```js
const img = genImage(600, 600, cx, cy, zoom, maxIter);
```

---

## 15. バッファを用意する

```go
var buf bytes.Buffer
```

これは **空のバッファ変数** を宣言しています。

JavaScriptなら `let buf = ...` に近いですが、Goでは `var` を使って型付きで宣言できます。

* `var 変数名 型`

です。

---

## 16. `if` の中で変数を作る書き方

```go
if err := png.Encode(&buf, img); err != nil {
	return "", err
}
```

これは Go らしい書き方です。

意味を分解するとこうです。

1. `png.Encode(&buf, img)` を実行
2. その戻り値を `err` に入れる
3. `err != nil` ならエラー処理する

JavaScript風に書くとこういうイメージです。

```js
const err = pngEncode(buf, img);
if (err != null) {
  return ["", err];
}
```

Goでは `if` の前半で変数を作れるのが特徴です。

---

## 17. Base64エンコードして返す

```go
encoded := base64.StdEncoding.EncodeToString(buf.Bytes())
return "data:image/png;base64," + encoded, nil
```

PNGのバイナリデータを Base64 文字列にして、ブラウザでそのまま表示できる Data URL として返しています。

JavaScriptならこうです。

```js
const encoded = toBase64(buf);
return ["data:image/png;base64," + encoded, null];
```

---

# 実際に画像を作る部分

## 18. `genImage`

```go
func genImage(w, h int, cx, cy, zoom float64, maxIter int) image.Image {
```

ここは `App` のメソッドではなく、普通の関数です。

### 違い

* メソッド: `func (a *App) ...`
* 普通の関数: `func ...`

つまりこれは `a` を使わない、独立した処理です。

---

## 19. 新しいRGBA画像を作る

```go
img := image.NewRGBA(image.Rect(0, 0, w, h))
```

これは幅 `w`、高さ `h` の空画像を作っています。

JavaScriptなら Canvas を作る感じに近いです。

---

## 20. 二重ループ

```go
for y := range h {
	for x := range w {
```

ここは少し注意です。

この書き方は **新しめの Go では整数に対する `range` が使える** ため成立します。
ただ、初心者向けにはこちらの形のほうが分かりやすいです。

```go
for y := 0; y < h; y++ {
	for x := 0; x < w; x++ {
```

JavaScriptならこうです。

```js
for (let y = 0; y < h; y++) {
  for (let x = 0; x < w; x++) {
```

### Goの `for`

Goには `while` がありません。
繰り返しは基本全部 `for` で書きます。

代表的には3種類です。

#### JavaScriptの普通の for に相当

```go
for i := 0; i < 10; i++ {
}
```

#### while 的な使い方

```go
for x < 10 {
}
```

#### range を使う

```go
for i := range arr {
}
```

---

## 21. 各ピクセルの計算

```go
rx, ry := pxToComplex(x, y, w, h, cx, cy, zoom)
iter, zx, zy := iterMandelbrot(rx, ry, maxIter)
img.Set(x, y, pixelColor(iter, maxIter, zx, zy))
```

ここでは、

1. 画面上の `x, y` を複素数平面の座標に変換
2. マンデルブロ計算をする
3. 結果に応じた色を設定

しています。

### 複数戻り値を複数変数で受ける

Goではこれが頻出です。

```go
rx, ry := ...
iter, zx, zy := ...
```

JavaScriptでは配列やオブジェクトで返しがちですが、Goはそのまま複数返せます。

---

# 複素数平面への変換

## 22. `pxToComplex`

```go
func pxToComplex(x, y, w, h int, cx, cy, zoom float64) (float64, float64) {
	rx := (float64(x)-float64(w)/2)/(0.5*zoom*float64(w)) + cx
	ry := (float64(y)-float64(h)/2)/(0.5*zoom*float64(h)) + cy
	return rx, ry
}
```

この関数は、

* 画像のピクセル座標
* マンデルブロ集合の座標

を対応付けています。

---

### 型変換 `float64(x)`

Goは型に厳しいです。

JavaScriptなら

```js
x - w / 2
```

とそのまま書けますが、Goでは

* `x` は `int`
* `w/2` も `int`
* 小数計算したいなら `float64` に変換

が必要です。

なので

```go
float64(x)
float64(w)
```

のように変換しています。

これは Go 初心者がかなりつまずく点です。

---

# マンデルブロ集合の反復計算

## 23. `iterMandelbrot`

```go
func iterMandelbrot(rx, ry float64, maxIter int) (int, float64, float64) {
	zx, zy := 0.0, 0.0
	iter := 0
	for zx*zx+zy*zy <= 4 && iter < maxIter {
		zx, zy = zx*zx-zy*zy+rx, 2*zx*zy+ry
		iter++
	}
	return iter, zx, zy
}
```

ここがマンデルブロ集合の核です。

---

### `zx, zy := 0.0, 0.0`

同時に2つの変数を作っています。

JavaScriptなら

```js
let zx = 0.0, zy = 0.0;
```

です。

---

### 条件付きループ

```go
for zx*zx+zy*zy <= 4 && iter < maxIter {
```

JavaScriptなら

```js
while (zx*zx + zy*zy <= 4 && iter < maxIter) {
```

に近いです。

Goには `while` がないので、これも `for` で書きます。

---

### 同時代入

```go
zx, zy = zx*zx-zy*zy+rx, 2*zx*zy+ry
```

これは Go の便利な書き方です。
右辺を先に全部計算してから、左辺にまとめて代入します。

JavaScriptだとこういうイメージです。

```js
[zx, zy] = [zx*zx - zy*zy + rx, 2*zx*zy + ry];
```

この書き方のおかげで、途中で `zx` を更新してしまって計算が壊れるのを防げます。

---

### `iter++`

これは JavaScript と同じで、1増やします。

---

# 色を決める部分

## 24. `pixelColor`

```go
func pixelColor(iter, maxIter int, zx, zy float64) color.Color {
```

この関数は、反復回数などからピクセルの色を決めます。

戻り値の `color.Color` は「色を表す型」です。

---

## 25. 集合の内部なら暗い色

```go
if iter == maxIter {
	return color.RGBA{R: 8, G: 8, B: 24, A: 255}
}
```

これは「最大回数まで発散しなかった点」は集合の内部とみなして、暗い色を返しています。

### `color.RGBA{...}`

これも構造体リテラルです。

JavaScriptなら

```js
return { R: 8, G: 8, B: 24, A: 255 };
```

っぽいです。

---

## 26. 色相の計算

```go
mod2 := zx*zx + zy*zy
mu := float64(iter) + 1 - math.Log(math.Log(math.Sqrt(mod2)))/math.Log(2)
t := mu / float64(maxIter)
h := math.Mod(360*3*t+220, 360)
```

ここは数学部分です。

* `mod2` … 複素数の大きさの二乗
* `mu` … スムーズカラーリング用の値
* `t` … 0〜1くらいに正規化した値
* `h` … 色相

### `math.Mod`

JavaScript の `%` に似ていますが、浮動小数点向けの余り計算です。

---

## 27. HSVからRGBへ変換

```go
col := colorful.Hsv(h, 0.9, 1.0)
r, g, b := col.RGB255()
return color.RGBA{R: r, G: g, B: b, A: 255}
```

ここでは

1. HSV色空間で色を作る
2. RGBに変換する
3. RGBA色として返す

という流れです。

JavaScriptで外部ライブラリを使って色を変換する感じに近いです。

---

# JavaScript初心者向けに、このGoコードをどう読むか

このコードは JavaScript の感覚で読むと、だいたいこうなります。

```js
class App {
  constructor() {
    this.ctx = null;
  }

  startup(ctx) {
    this.ctx = ctx;
  }

  async OpenSaveDialog() {
    const options = {
      DefaultFilename: "mandelbrot.png",
      Filters: [
        { DisplayName: "PNG画像", Pattern: "*.png" },
        { DisplayName: "全てのファイル", Pattern: "*.*" }
      ]
    };
    return await wails.SaveFileDialog(this.ctx, options);
  }

  SaveB64Image(dataURL, filename) {
    const prefix = "data:image/png;base64,";
    if (!dataURL.startsWith(prefix)) {
      throw new Error("invalid");
    }
    const base64Data = dataURL.slice(prefix.length);
    const imgData = decodeBase64(base64Data);
    writeFile(filename, imgData);
  }

  GenImage(cx, cy, zoom, maxIter) {
    const img = genImage(600, 600, cx, cy, zoom, maxIter);
    const pngBytes = encodePng(img);
    const encoded = toBase64(pngBytes);
    return "data:image/png;base64," + encoded;
  }
}
```

Goは JavaScript よりも、

* 型を明示する
* エラーを戻り値で扱う
* クラスではなく struct + メソッドを使う
* 複数の戻り値を普通に返す

という違いがあります。

---

# このコードで特に覚えるべきGo文法

初心者向けに重要なものだけ絞ると、次の8個です。

## 1. 変数宣言

```go
x := 10
```

新しい変数を作る。型は自動推論。

---

## 2. 関数定義

```go
func add(a int, b int) int {
	return a + b
}
```

---

## 3. 同じ型の引数はまとめて書ける

```go
func f(a, b int, c string)
```

---

## 4. 戻り値を複数返せる

```go
func f() (string, error)
```

---

## 5. エラーは `if err != nil`

```go
v, err := someFunc()
if err != nil {
	return err
}
```

---

## 6. struct はデータの箱

```go
type App struct {
	ctx context.Context
}
```

---

## 7. メソッドはレシーバ付き

```go
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}
```

---

## 8. `for` は万能

```go
for i := 0; i < 10; i++ {}
for x < 10 {}
```

---

# このコードの処理の流れ

最後に、処理の流れを簡単にまとめます。

1. Wails が `App` を作る
2. 起動時に `startup(ctx)` が呼ばれて `ctx` を保存
3. フロントエンドが `GenImage(...)` を呼ぶ
4. Go側でマンデルブロ画像を計算
5. PNGに変換
6. Base64文字列にしてフロントエンドへ返す
7. 必要なら `OpenSaveDialog()` で保存先を選ぶ
8. `SaveB64Image(...)` でファイル保存する

---

# 補足: このコードで少し気をつけたい点

この部分です。

```go
for y := range h {
	for x := range w {
```

これは新しめの Go では使える書き方ですが、初心者向けには次の形のほうが分かりやすいです。

```go
for y := 0; y < h; y++ {
	for x := 0; x < w; x++ {
```




