# テキストエディタを作成してみよう

Wailsを使ったアプリのサンプルです。

## Live Development

Wailsをインストールした上で、下記のコマンドを実行するとプログラムを実行できます。

```sh
wails dev
```

## Go言語が分からないという方へ

下記のようなプロンプトを、生成AIに与えると、分かりやすく解説してくれます。

```md
Go言語の初心者です。
次のGo言語のコードを、JavaScriptで表現すると、どうなりますか？
一行ずつ対比させて説明してください。
```

## app.goをJS風に解説したもの

以下は、[src/ch4/wails-notepad/app.go](src/ch4/wails-notepad/app.go)の内容を上記のプロンプトと一緒に、ChatGPTに与えたものです。

Wails の `app.go` は、**Goで書くバックエンドの本体**です。
なので JavaScript にそのまま置き換えるというより、**「同じ役割を JavaScript で書くならこうなる」**と考えるのが自然です。

まず、全体を JavaScript っぽく書くとこんな感じです。

```javascript
import fs from "node:fs/promises";

// Wailsの核となるAppクラスを定義
class App {
  constructor() {
    this.ctx = null;
  }

  // アプリ起動時に呼び出されるメソッド
  startup(ctx) {
    this.ctx = ctx;
  }

  // ファイルの保存機能
  async Save(text) {
    const filename = await saveFileDialog(this.ctx, {});
    if (!filename) {
      throw new Error("ファイルの保存に失敗");
    }

    await fs.writeFile(filename, text, "utf-8");
    return filename;
  }

  // ファイルの読み込み機能
  async Load() {
    const filename = await openFileDialog(this.ctx, {});
    if (!filename) {
      throw new Error("ファイルの読み込みに失敗");
    }

    const data = await fs.readFile(filename, "utf-8");
    return data;
  }
}

// Appを生成する関数
function NewApp() {
  return new App();
}
```

ただし、ここで使っている `saveFileDialog()` や `openFileDialog()` は、**JavaScript標準の関数ではありません**。
Go の `runtime.SaveFileDialog` / `runtime.OpenFileDialog` に相当する処理を、JavaScript側で説明用に仮置きしたものです。

---

## まず大事な違い

この Go の `app.go` は、**Wails の Go 側コード**です。
Wails では普通、JavaScript 側はこの `Save()` や `Load()` を**呼び出す側**になります。

つまり実務ではこうです。

* **Go (`app.go`)**
  ファイルダイアログを開く、ファイル保存する、ファイル読む
* **JavaScript / フロントエンド**
  `Save(text)` や `Load()` を呼び出して結果を受け取る

なので、今回の「JavaScriptで表現」は、
**Goの書き方をJSの書き方に置き換えるとどう見えるか**、という理解用です。

---

## 一行ずつ対比して説明

---

### 1. パッケージ宣言

#### Go

```go
package main
```

#### JavaScript

```javascript
// JavaScriptには package main のような書き方はない
```

#### 説明

Go ではこのファイルが `main` パッケージに属していることを示します。
JavaScript にはこの概念はありません。
JS では「ファイル」や「モジュール」単位で扱います。

---

### 2. import ブロック

#### Go

```go
import (
	"context"
	"fmt"
	"os"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)
```

#### JavaScript

```javascript
import fs from "node:fs/promises";
```

#### 説明

Go では必要なパッケージをまとめて `import` します。
JavaScript でも `import` を使いますが、読み込むものは少し違います。

対応のイメージはこうです。

* `context` → JS には直接対応する標準機能はない
* `fmt` → JS では `Error` やテンプレート文字列で代用することが多い
* `os` → Node.js の `fs` などで代用
* `runtime` → Wails 固有のAPI。JS標準にはない

---

### 3. 構造体定義

#### Go

```go
type App struct {
	ctx context.Context
}
```

#### JavaScript

```javascript
class App {
  constructor() {
    this.ctx = null;
  }
}
```

#### 説明

Go の `struct` は、**データをまとめる入れ物**です。
JavaScript なら、ふつうは `class` と `constructor` で表します。

Go の

* `App` という型を作る
* 中に `ctx` というフィールドを持つ

という意味が、JS では

* `App` クラスを作る
* `this.ctx` を持たせる

に相当します。

---

### 4. コンストラクタ関数

#### Go

```go
func NewApp() *App {
	return &App{}
}
```

#### JavaScript

```javascript
function NewApp() {
  return new App();
}
```

#### 説明

Go にはクラスの `constructor` という仕組みがないので、
よく `NewXxx()` という関数を作ってインスタンスを返します。

Go の

```go
return &App{}
```

は、

* `App` 構造体を新しく作る
* そのポインタを返す

という意味です。

JavaScript では `new App()` と書けば新しいインスタンスを返せます。

---

### 5. startup メソッド定義

#### Go

```go
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}
```

#### JavaScript

```javascript
startup(ctx) {
  this.ctx = ctx;
}
```

#### 説明

Go の

```go
func (a *App) ...
```

は、**App 型に属するメソッド**を定義しています。
JavaScript ではクラスの中にそのままメソッドを書きます。

対応はこうです。

* `a *App` → `this`
* `ctx context.Context` → `ctx`
* `a.ctx = ctx` → `this.ctx = ctx`

Wails ではこの `startup()` が起動時に呼ばれ、
そこで受け取った `ctx` を後でダイアログ表示などに使います。

---

### 6. Save メソッド定義

#### Go

```go
func (a *App) Save(text string) (string, error) {
```

#### JavaScript

```javascript
async Save(text) {
```

#### 説明

Go では引数と戻り値の型を明示します。

* 引数: `text string`
* 戻り値: `(string, error)`

JavaScript は型を書かないので、普通はこうなります。

ただし Go の `error` 戻り値は、JS ではふつう **例外** で表します。
またファイル操作は非同期にすることが多いので `async` を付けるのが自然です。

---

### 7. 保存ダイアログを開く

#### Go

```go
filename, err := runtime.SaveFileDialog(a.ctx, runtime.SaveDialogOptions{})
```

#### JavaScript

```javascript
const filename = await saveFileDialog(this.ctx, {});
```

#### 説明

Go では

* `filename`
* `err`

の2つを受け取っています。
Go は「戻り値を複数返す」文化なのでこう書きます。

JavaScript では普通、

* 成功時は値を返す
* 失敗時は例外を投げる

という形です。
そのため `filename` だけ受け取り、失敗は `catch` や `throw` で扱います。

---

### 8. ダイアログエラー判定

#### Go

```go
if err != nil {
	return "", fmt.Errorf("ファイルの保存に失敗: %v", err)
}
```

#### JavaScript

```javascript
if (!filename) {
  throw new Error("ファイルの保存に失敗");
}
```

#### 説明

Go では `err != nil` を毎回チェックします。
JavaScript では例外が主流です。

ただしここは少し注意点があります。

Go の `SaveFileDialog()` は、状況によっては

* エラー
* キャンセル
* 正常終了

を分けて扱えます。

JS に直すなら実際にはこういう形もありです。

```javascript
try {
  const filename = await saveFileDialog(this.ctx, {});
} catch (err) {
  throw new Error(`ファイルの保存に失敗: ${err.message}`);
}
```

---

### 9. ファイルへ書き込む

#### Go

```go
err = os.WriteFile(filename, []byte(text), 0644)
```

#### JavaScript

```javascript
await fs.writeFile(filename, text, "utf-8");
```

#### 説明

ここはかなり対応が分かりやすいです。

Go では

* `filename` に
* `text` をバイト列にして
* パーミッション `0644` で保存

しています。

JavaScript の Node.js では `fs.writeFile()` を使います。
文字列のまま書けるので `[]byte(text)` は不要です。

なお、`0644` のような権限指定は JS 側では省略されがちです。
必要なら options で指定できます。

---

### 10. 書き込みエラー判定

#### Go

```go
if err != nil {
	return "", fmt.Errorf("ファイルの書き込みに失敗: %v", err)
}
```

#### JavaScript

```javascript
// fs.writeFile が失敗したら例外になる
```

または明示的に書くなら:

```javascript
try {
  await fs.writeFile(filename, text, "utf-8");
} catch (err) {
  throw new Error(`ファイルの書き込みに失敗: ${err.message}`);
}
```

#### 説明

Go は毎回 `err` を見ます。
JS は失敗時に `throw` されるので、必要なら `try/catch` で包みます。

---

### 11. 保存成功時の戻り値

#### Go

```go
return filename, nil
```

#### JavaScript

```javascript
return filename;
```

#### 説明

Go では `(string, error)` を返すので、

* 正常時: `filename, nil`
* 異常時: `"", error`

という形です。

JavaScript では通常、

* 正常時: 値を返す
* 異常時: 例外を投げる

なので `return filename` だけです。

---

## Load 側も同じ考え方です

---

### 12. Load メソッド定義

#### Go

```go
func (a *App) Load() (string, error) {
```

#### JavaScript

```javascript
async Load() {
```

#### 説明

`Save()` と同じです。
Go の `(string, error)` は、JS では「値を返す + 失敗時は例外」と考えると分かりやすいです。

---

### 13. 開くダイアログを表示

#### Go

```go
filename, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{})
```

#### JavaScript

```javascript
const filename = await openFileDialog(this.ctx, {});
```

#### 説明

`SaveFileDialog` が `OpenFileDialog` に変わっただけです。
考え方は同じです。

---

### 14. ダイアログエラー判定

#### Go

```go
if err != nil {
	return "", fmt.Errorf("ファイルの読み込みに失敗: %v", err)
}
```

#### JavaScript

```javascript
if (!filename) {
  throw new Error("ファイルの読み込みに失敗");
}
```

#### 説明

Go の `error` チェックを、JS の例外や null チェックに置き換えています。

---

### 15. ファイルを読む

#### Go

```go
data, err := os.ReadFile(filename)
```

#### JavaScript

```javascript
const data = await fs.readFile(filename, "utf-8");
```

#### 説明

Go の `os.ReadFile()` はバイト列を返します。
JavaScript の `fs.readFile(..., "utf-8")` は文字列を返します。

なので JS では後ろの `string(data)` が不要になります。

---

### 16. 読み込みエラー判定

#### Go

```go
if err != nil {
	return "", fmt.Errorf("ファイルの読み込みに失敗: %v", err)
}
```

#### JavaScript

```javascript
// fs.readFile が失敗したら例外になる
```

または:

```javascript
try {
  const data = await fs.readFile(filename, "utf-8");
} catch (err) {
  throw new Error(`ファイルの読み込みに失敗: ${err.message}`);
}
```

#### 説明

これも `Save()` と同じです。

---

### 17. 読み込んだ内容を返す

#### Go

```go
return string(data), nil
```

#### JavaScript

```javascript
return data;
```

#### 説明

Go の `data` はバイト列なので `string(data)` が必要です。
JavaScript では最初から文字列として読んでいるので、そのまま返せます。

---

# Go と JavaScript の考え方の違いをまとめると

このコードで大事なのは次の対応です。

### 1. struct ↔ class

Go:

```go
type App struct { ... }
```

JS:

```javascript
class App { ... }
```

---

### 2. メソッドレシーバ ↔ this

Go:

```go
func (a *App) Save(...)
```

JS:

```javascript
Save(...) { ... }
```

中では `a` の代わりに `this` を使います。

---

### 3. `(値, error)` ↔ `return / throw`

Go:

```go
return filename, nil
return "", err
```

JS:

```javascript
return filename;
throw new Error(...);
```

---

### 4. 同期っぽいGoコード ↔ 非同期のJS

Go のファイル処理はこの例では普通の関数呼び出しですが、
JavaScript ではファイル操作を `async/await` にすることが多いです。

---

# Wails での実際の見え方

Wails では、あなたがこの Go コードを書いたあと、
フロントエンドの JavaScript / TypeScript からは、だいたいこんな感じで呼びます。

```javascript
import { Save, Load } from "../wailsjs/go/main/App";

async function test() {
  const filename = await Save("こんにちは");
  const text = await Load();
  console.log(filename, text);
}
```

つまり、

* `app.go` を JavaScript に書き換えることは通常しない
* JavaScript 側は `Save()` や `Load()` を呼ぶ

という理解が、Wails ではいちばん実務的です。

---

# 初心者向けに超ざっくり言うと

この Go コードは JavaScript 感覚でいうと、

* `App` というクラスを作って
* `startup()` で初期化して
* `Save(text)` で保存
* `Load()` で読み込み

という形です。

Go らしいところは主にこの3つです。

* `struct` を使う
* `func (a *App)` でメソッドを書く
* `error` を戻り値で返す


