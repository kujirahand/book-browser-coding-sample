# Tauriでファイルを読み出すプログラムを作ろう

Tauriで、デスクトップに配置したテキストファイル「sample.txt」を読み出して、表示するツールを作ってみましょう。

## ライブラリのインストール

```sh
cd tauri-file-reader
npm install
npm run tauri dev
```

## Rustのプログラムが分からないという方へ

Rustのコードが難しいと感じる場合は、生成AIの力を借りて、Rustのコードを解説してもらうと良いでしょう。

```md
Rust初心者です。
以下は、Tauriでライブラリを記述するコードです。
分かりやすく、JavaScriptで書くとどうなるのか、部分ごとに教えて。
--------------
<Rustのコード>
```

上記のプロンプトをChatGPTに与えて、[src-tauri/src/lib.rs](src-tauri/src/lib.rs) を解説させると、次のようになります。

もちろんです。
これは **「Rustで書いた Tauri のバックエンド処理を、JavaScriptの感覚でどう見るか」** という話として読むと分かりやすいです。

ただし先に大事な点だけ言うと、**Tauri のこの部分は本来 Rust でしか書けません**。
なのでここでは、**同じ役割を JavaScript で表すとこんな感じ**、という対応で説明します。

---

## 全体像

この Rust コードは、ざっくり言うと次のことをしています。

1. フロントエンドから呼べる `read_file` 関数を作る
2. その関数を Tauri に登録する
3. アプリを起動する

JavaScriptっぽく全体を書くと、イメージはこんな感じです。

```js
import path from "path";
import fs from "fs";

// フロントエンドから呼べる関数
function readFile(app, filename) {
  const desktopDir = app.path.desktopDir();
  const filePath = path.join(desktopDir, filename);

  try {
    return fs.readFileSync(filePath, "utf-8");
  } catch (err) {
    return `ファイルが読めません。デスクトップに${filename}を配置してください: ${err}`;
  }
}

// アプリを起動
function run() {
  const builder = new TauriBuilder();

  builder.plugin(openerPlugin());
  builder.invokeHandler({
    read_file: readFile,
  });

  builder.run();
}
```

これは実際の Tauri の JavaScript API そのものではなく、**構造を理解するための対応図**です。

---

# 1. `use tauri::Manager;`

Rust:

```rust
use tauri::Manager;
```

JavaScriptで感覚的に近いもの:

```js
import { Manager } from "tauri";
```

### 意味

Rust の `use` は、JavaScript の `import` に近いです。
ここでは `Manager` という機能を使えるようにしています。

### なぜ必要？

このコードでは次の部分で使っています。

```rust
app.path().desktop_dir()
```

`app` から `path()` を呼べるのは、`Manager` が関係しています。
JavaScriptでいえば、**便利メソッドを追加するモジュールを読み込んでいる**感じです。

---

# 2. `#[tauri::command]`

Rust:

```rust
#[tauri::command]
```

JavaScriptっぽい意味:

```js
// この関数はフロントエンドから呼び出せます
```

あるいは、雰囲気としてはこうです。

```js
registerCommand("read_file", readFile);
```

### 意味

この属性が付いた関数は、フロントエンド側から `invoke("read_file", ...)` で呼べるようになります。

つまりこれは、JavaScriptでいうと

* 公開APIにする
* RPCとして公開する
* フロントから呼べる関数として登録対象にする

という目印です。

---

# 3. 関数定義 `fn read_file(...) -> String`

Rust:

```rust
fn read_file(app: tauri::AppHandle, filename: &str) -> String {
```

JavaScriptで書くと:

```js
function readFile(app, filename) {
```

### 対応関係

* `fn` → `function`
* `read_file` → `readFile` っぽく書くことが多い
* `app: tauri::AppHandle` → `app`
* `filename: &str` → `filename`
* `-> String` → 戻り値が文字列

### Rustらしい点

Rust は型をきっちり書きます。

```rust
filename: &str
```

は、**文字列への参照**です。
JavaScript なら型を書かないので、ただの `filename` になります。

---

# 4. デスクトップフォルダを取得する部分

Rust:

```rust
let desktop_dir = app.path().desktop_dir().unwrap();
```

JavaScriptで感覚的に書くと:

```js
const desktopDir = app.path.desktopDir();
```

あるいは、失敗の可能性も含めるなら:

```js
const desktopDir = app.path.desktopDir();
if (!desktopDir) {
  throw new Error("デスクトップフォルダが取得できません");
}
```

### 意味

* `app.path()` でパス関連の機能を取り出す
* `desktop_dir()` でデスクトップフォルダを取得する
* `unwrap()` で「失敗していたら強制終了、成功なら中身を取り出す」

### `unwrap()` を JavaScript感覚でいうと

かなり乱暴に言うと、こういう感覚です。

```js
const desktopDir = getDesktopDir();
if (desktopDir == null) {
  throw new Error("値がありません");
}
```

Rust では `desktop_dir()` は「成功するかもしれないし失敗するかもしれない値」を返します。
`unwrap()` はそれを **強引に取り出す** 操作です。

初心者向けには、こう覚えるとよいです。

* `unwrap()` = 「ある前提で取り出す」
* 失敗したらその場でエラー終了

---

# 5. ファイルパスを作る部分

Rust:

```rust
let file_path = desktop_dir.join(filename);
```

JavaScriptで書くと:

```js
const filePath = path.join(desktopDir, filename);
```

### 意味

デスクトップフォルダとファイル名をつないで、完全なパスを作っています。

たとえば `filename` が `memo.txt` なら、

* Rust: `desktop_dir.join("memo.txt")`
* JS: `path.join(desktopDir, "memo.txt")`

となります。

---

# 6. ファイルを読む部分

Rust:

```rust
std::fs::read_to_string(file_path)
```

JavaScriptで書くと:

```js
fs.readFileSync(filePath, "utf-8")
```

または非同期なら:

```js
await fs.promises.readFile(filePath, "utf-8")
```

### 意味

ファイルの内容を文字列として読み込みます。

Rust の `read_to_string` は、その名の通り
**「ファイルを読んで文字列にする」** 関数です。

---

# 7. エラー処理 `unwrap_or_else(...)`

Rust:

```rust
.unwrap_or_else(
    |err| format!(
        "ファイルが読めません。デスクトップに{filename}を配置してください: {err}"))
```

JavaScriptで書くと、だいたいこうです。

```js
try {
  return fs.readFileSync(filePath, "utf-8");
} catch (err) {
  return `ファイルが読めません。デスクトップに${filename}を配置してください: ${err}`;
}
```

### 意味

Rust の `read_to_string(file_path)` は、成功なら内容、失敗ならエラーを返します。
`unwrap_or_else(...)` は、

* 成功したらその値を返す
* 失敗したら指定した処理を実行する

というものです。

### `|err|` とは？

これは JavaScript の引数に相当します。

Rust:

```rust
|err| ...
```

JavaScript:

```js
(err) => ...
```

つまり、

```rust
|err| format!("...")
```

は、JavaScript なら

```js
(err) => `...`
```

みたいな感じです。

---

# 8. `format!` マクロ

Rust:

```rust
format!(
    "ファイルが読めません。デスクトップに{filename}を配置してください: {err}"
)
```

JavaScriptで書くと:

```js
`ファイルが読めません。デスクトップに${filename}を配置してください: ${err}`
```

### 意味

文字列の中に変数を埋め込んで、新しい文字列を作っています。

* Rust の `format!`
* JavaScript の テンプレートリテラル `` `...${...}` ``

はかなり近いです。

---

# 9. `run()` 関数

Rust:

```rust
pub fn run() {
```

JavaScriptで書くと:

```js
export function run() {
```

### 意味

`run` という関数を公開しています。

* `pub` = 外から使える
* `fn` = 関数定義

なので、JavaScriptの `export function` に近いです。

---

# 10. `#[cfg_attr(mobile, tauri::mobile_entry_point)]`

Rust:

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
```

JavaScriptで厳密対応はしにくいですが、感覚としてはこうです。

```js
// モバイル向けビルド時には、この関数をエントリーポイントとして扱う
```

### 意味

これは **条件付きで属性を付ける** 仕組みです。
`mobile` のときだけ `tauri::mobile_entry_point` を付ける、という意味です。

JavaScriptにはこの書き方そのものはありません。
なのでここは、

* ビルド条件によって設定を変える
* 環境ごとにエントリーポイントを調整する

ための Rust / Tauri 特有の記法と思って大丈夫です。

---

# 11. `tauri::Builder::default()`

Rust:

```rust
tauri::Builder::default()
```

JavaScriptっぽく書くと:

```js
const builder = new TauriBuilder();
```

### 意味

Tauri アプリの設定を組み立てるための Builder を作っています。

これは JavaScript でいうと、設定オブジェクトやアプリインスタンスを作る感覚です。

---

# 12. プラグイン登録

Rust:

```rust
.plugin(tauri_plugin_opener::init())
```

JavaScriptで書くと:

```js
builder.plugin(openerPlugin());
```

### 意味

`opener` プラグインを有効にしています。

これは、JavaScriptフレームワークでよくある

```js
app.use(plugin)
```

に近いです。

---

# 13. `invoke_handler(...)`

Rust:

```rust
.invoke_handler(tauri::generate_handler![
    read_file
])
```

JavaScriptで書くと:

```js
builder.invokeHandler({
  read_file: readFile
});
```

### 意味

フロントエンドから呼べる関数を登録しています。

ここがかなり重要です。
`#[tauri::command]` を付けただけでは足りなくて、**実際に登録する** 必要があります。

JavaScriptの感覚でいうと、

```js
api.register("read_file", readFile);
```

みたいなものです。

### `generate_handler!` とは？

これは Rust のマクロで、指定した関数一覧から Tauri 用のハンドラを作ってくれます。

つまり、

```rust
tauri::generate_handler![read_file]
```

は、イメージとしては

```js
{
  read_file: readFile
}
```

のような登録表を自動生成している感じです。

---

# 14. アプリ実行

Rust:

```rust
.run(tauri::generate_context!())
.expect("error while running tauri application");
```

JavaScriptで書くと:

```js
builder.run();
```

失敗も意識するなら:

```js
try {
  builder.run();
} catch (err) {
  throw new Error("error while running tauri application");
}
```

### 意味

ここで Tauri アプリを実際に起動しています。

* `generate_context!()` は Tauri の設定情報を読み込むためのもの
* `run(...)` で起動
* `expect(...)` で失敗時にメッセージを出して終了

### `expect(...)` とは？

`unwrap()` に似ていますが、**失敗時のメッセージを自分で指定できる** 版です。

Rust:

```rust
something.expect("エラーです");
```

JavaScript感覚では:

```js
if (!something) {
  throw new Error("エラーです");
}
```

に近いです。

---

# 15. 全体をもう一度、対応付きで並べる

## Rust

```rust
use tauri::Manager;

#[tauri::command]
fn read_file(app: tauri::AppHandle, filename: &str) -> String {
    let desktop_dir = app.path().desktop_dir().unwrap();
    let file_path = desktop_dir.join(filename);
    std::fs::read_to_string(file_path).unwrap_or_else(
        |err| format!(
            "ファイルが読めません。デスクトップに{filename}を配置してください: {err}"))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            read_file
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## JavaScriptイメージ

```js
import path from "path";
import fs from "fs";

function readFile(app, filename) {
  const desktopDir = app.path.desktopDir();
  const filePath = path.join(desktopDir, filename);

  try {
    return fs.readFileSync(filePath, "utf-8");
  } catch (err) {
    return `ファイルが読めません。デスクトップに${filename}を配置してください: ${err}`;
  }
}

export function run() {
  const builder = new TauriBuilder();

  builder.plugin(openerPlugin());

  builder.invokeHandler({
    read_file: readFile,
  });

  builder.run();
}
```

---

# 16. このコードの本質を一言で言うと

この Rust コードは、JavaScriptの感覚では次の一文になります。

**「フロントエンドから呼べる `read_file` というバックエンド関数を登録して、Tauri アプリを起動している」**

です。

---

# 17. Rust初心者向けに特に押さえるポイント

このコードでまず覚えるとよいのはこの5つです。

* `use` は JavaScript の `import` に近い
* `fn` は `function`
* `#[tauri::command]` は「フロントから呼べる関数」の印
* `unwrap()` / `expect()` は「失敗ならその場で止める」
* `invoke_handler(...)` で公開関数を登録する


