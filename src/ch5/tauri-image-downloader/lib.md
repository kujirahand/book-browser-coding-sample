# src-tauri/src/lib.rs の解説

このコードは、**Tauri アプリの起動設定**を書くための Rust コードです。

JavaScriptでたとえると、これは「アプリ起動時に、使う機能を登録して、フロントエンドから呼べる関数を設定して、最後にアプリを起動する」部分です。

まず全体像から言うと、このコードは次のことをしています。

1. `downloader` と `html_query` という別ファイルの機能を使えるようにする
2. Tauri の設定を組み立てる
3. フロントエンドから呼べる Rust 関数を登録する
4. アプリを起動する

---

## コード全体

```rust
// 前の手順で作成したモジュールを使うことを宣言 --- (*1)
mod downloader;
mod html_query;

// TauriアプリにRustコマンドを登録する --- (*2)
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            html_query::collect_images, // 画像URLを収集する関数 --- (*3)
            downloader::download // 画像URLをダウンロードする関数)
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

# まず JavaScript で似た形にすると

Rust の細かい文法をいったん忘れて、JavaScript風に書くと、だいたいこんなイメージです。

```javascript
import * as downloader from "./downloader";
import * as html_query from "./html_query";

export function run() {
  Tauri.Builder.default()
    .plugin(opener.init())
    .invokeHandler([
      html_query.collect_images,
      downloader.download
    ])
    .run(Tauri.generateContext())
    .expect("error while running tauri application");
}
```

もちろん実際の JavaScript の Tauri コードとは少し違いますが、**意味のイメージ**はかなり近いです。

---

# 1行ずつ見ていきます

## `mod downloader;`

```rust
mod downloader;
```

これは、**`downloader` というモジュールを使います**、という宣言です。

Rust では、機能をファイルやまとまりごとに分けて管理します。
この `mod downloader;` は、たとえば `downloader.rs` というファイルがあって、その中の関数や定義をこの `lib.rs` から使えるようにする意味です。

### JavaScript で似た感覚

JavaScript ならこういう気分です。

```javascript
import "./downloader.js";
```

あるいは、より感覚的には、

```javascript
import * as downloader from "./downloader.js";
```

に近いです。

### Rust と JavaScript の違い

JavaScript では `import` で読み込みますが、Rust ではまず `mod` で「このモジュールがあります」と宣言します。

Rust では次の2段階で考えると分かりやすいです。

* `mod downloader;`

  * モジュールを宣言する
* `downloader::download`

  * その中の関数を使う

---

## `mod html_query;`

```rust
mod html_query;
```

これも同じです。
`html_query.rs` というファイルの機能を使えるようにしています。

JavaScript なら、

```javascript
import * as html_query from "./html_query.js";
```

のような感覚です。

---

# Rust の `mod` とは何か

JavaScript初心者向けにかなりざっくり言うと、

* **JavaScript のモジュール** → `import/export`
* **Rust のモジュール** → `mod` と `pub`

です。

特に Rust では、外から使いたい関数には `pub` を付けます。
たとえば `html_query.rs` 側では、こんな感じになっているはずです。

```rust
pub fn collect_images() {
    // ...
}
```

この `pub` は、JavaScript の `export` に近いです。

### 対比

Rust:

```rust
pub fn collect_images() { }
```

JavaScript:

```javascript
export function collect_images() { }
```

---

# `#[cfg_attr(mobile, tauri::mobile_entry_point)]`

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
```

これは **属性(attribute)** と呼ばれる Rust の特別な記法です。
`#[]` で書きます。

かなり初心者には難しい部分ですが、ここでは、

**「条件によって、この関数に特別な意味を付ける設定」**

くらいで十分です。

### ざっくり意味

* `mobile` 環境なら
* `tauri::mobile_entry_point` という属性を付ける

つまり、**モバイル用の Tauri アプリとして動かすときの入口にする**、という意味です。

### JavaScript でたとえると

JavaScript には完全に同じ文法はありません。
雰囲気としては、フレームワークが使うメタ情報です。

たとえば React や Next.js の「この関数は特別な役割を持つ」といった仕組みに少し似ています。

あるいは疑似コードで書くなら、

```javascript
@mobileEntryPoint
function run() {
}
```

みたいなイメージです。
ただし、JavaScript の標準文法そのものではありません。

### ここで大事なのは

この行は、**関数の中身の処理を書くものではなく、関数に補足情報を与えるもの**です。

---

# `pub fn run() { ... }`

```rust
pub fn run() {
```

これは関数定義です。

### 分解すると

* `pub`

  * 外部から使えるようにする
* `fn`

  * 関数を定義する
* `run`

  * 関数名
* `()`

  * 引数なし
* `{ ... }`

  * 関数の本体

### JavaScript との対比

Rust:

```rust
pub fn run() {
}
```

JavaScript:

```javascript
export function run() {
}
```

かなり似ています。

---

## Rust の `fn` と JavaScript の `function`

JavaScript では関数はこう書きます。

```javascript
function run() {
}
```

Rust ではこうです。

```rust
fn run() {
}
```

つまり、

* JavaScript → `function`
* Rust → `fn`

です。

---

## `pub` は JavaScript の `export` に近い

Rust の `pub` は、その関数や変数を外から使えるようにする印です。

Rust:

```rust
pub fn run() {
}
```

JavaScript:

```javascript
export function run() {
}
```

かなり近い役割です。

---

# `tauri::Builder::default()`

```rust
tauri::Builder::default()
```

ここから Tauri の設定を組み立てています。

### `::` は何？

Rust で `::` は、**どこにあるものかを指定する記号**です。

たとえば、

```rust
tauri::Builder
```

は、
「`tauri` の中にある `Builder`」という意味です。

### JavaScript で似た感覚

JavaScript ならドット `.` を使う場面に近いです。

```javascript
Tauri.Builder
```

みたいな感覚です。

ただし Rust では、

* モジュール
* 型
* 関数
* 関連関数

などを区切るのに `::` を使います。

---

## `default()` は「初期状態を作る」

```rust
tauri::Builder::default()
```

は、Tauri の `Builder` を初期状態で作る、という意味です。

JavaScript ならこんな感じです。

```javascript
const builder = Tauri.Builder.default();
```

あるいはクラスを使う感じで近づけると、

```javascript
const builder = new Builder();
```

みたいな感覚です。

---

# メソッドチェーン

ここから先はこの形になっています。

```rust
tauri::Builder::default()
    .plugin(...)
    .invoke_handler(...)
    .run(...)
    .expect(...);
```

これは **メソッドチェーン** です。

JavaScript でもよくあります。

```javascript
builder
  .plugin(...)
  .invokeHandler(...)
  .run()
  .expect(...);
```

つまり、

1. Builder を作る
2. plugin を追加する
3. invoke_handler を設定する
4. run で起動する
5. expect でエラー時のメッセージを決める

という流れです。

---

# `.plugin(tauri_plugin_opener::init())`

```rust
.plugin(tauri_plugin_opener::init())
```

これは Tauri にプラグインを追加しています。

### 意味

`tauri_plugin_opener` というプラグインを初期化して、アプリに組み込んでいます。

`opener` は一般に、URL やファイルを開くための機能に使われます。

### JavaScript でたとえると

```javascript
builder.plugin(opener.init());
```

のような感じです。

---

## `tauri_plugin_opener::init()`

ここでも `::` が出てきます。

```rust
tauri_plugin_opener::init()
```

これは
**`tauri_plugin_opener` の中にある `init` 関数を呼ぶ**
という意味です。

JavaScript なら、

```javascript
tauri_plugin_opener.init()
```

に近いです。

---

# `.invoke_handler(...)`

```rust
.invoke_handler(tauri::generate_handler![
    html_query::collect_images,
    downloader::download
])
```

ここがとても大事です。

これは、**フロントエンドの JavaScript から呼び出せる Rust の関数を登録する部分**です。

たとえばフロントエンドから

```javascript
invoke("collect_images")
```

のように呼べるようにするための設定です。

---

## `tauri::generate_handler![ ... ]`

ここで `!` が出てきています。

```rust
tauri::generate_handler![ ... ]
```

Rust の `!` は、**マクロ** を表すことが多いです。

### マクロとは

初心者向けに言うと、
**「普通の関数より少し特別で、コードを組み立てるための仕組み」**
です。

JavaScript にはほぼ同じものはありません。

感覚的には、

* 関数のように見える
* でも内部ではコード生成っぽいことをする

仕組みです。

### よく見る例

Rust では `println!()` もマクロです。

```rust
println!("hello");
```

なので、

```rust
generate_handler![ ... ]
```

も「Tauri 用の特別な仕組み」だと思えば大丈夫です。

---

## `[...]` で関数の一覧を渡している

```rust
tauri::generate_handler![
    html_query::collect_images,
    downloader::download
]
```

これは登録したい関数を並べています。

### JavaScript なら配列っぽい見た目

かなり見た目は JavaScript の配列に近いです。

```javascript
[
  html_query.collect_images,
  downloader.download
]
```

に似ています。

ただし Rust では、これは普通の配列というより、**マクロへの入力**です。

---

## `html_query::collect_images`

```rust
html_query::collect_images
```

これは
**`html_query` モジュールの中にある `collect_images` 関数**
という意味です。

JavaScript なら、

```javascript
html_query.collect_images
```

に近いです。

---

## `downloader::download`

```rust
downloader::download
```

これも同じです。

**`downloader` モジュールの中の `download` 関数**です。

JavaScript なら、

```javascript
downloader.download
```

です。

---

# `.run(tauri::generate_context!())`

```rust
.run(tauri::generate_context!())
```

ここで実際に Tauri アプリを起動しています。

### `run(...)`

`run` は「実行する」「起動する」です。

JavaScript なら、

```javascript
builder.run(...)
```

のような感覚です。

---

## `tauri::generate_context!()`

これも `!` が付いているのでマクロです。

これは Tauri アプリを動かすために必要な**設定情報（context）を生成する**ものです。

初心者向けには、

**「Tauri が起動に必要な情報をまとめて作ってくれるもの」**

と思えば大丈夫です。

JavaScript 的には、

```javascript
Tauri.generateContext()
```

っぽいイメージです。

ただし実際には Rust のマクロです。

---

# `.expect("error while running tauri application");`

```rust
.expect("error while running tauri application");
```

これはとても Rust らしい書き方です。

### 意味

`run(...)` の結果が失敗だったら、このメッセージを出して異常終了する、という意味です。

### JavaScript でたとえると

JavaScript ならこんな雰囲気です。

```javascript
const result = builder.run();
if (result is error) {
  throw new Error("error while running tauri application");
}
```

Rust では、失敗する可能性がある値を `Result` という型で扱うことが多いです。
`expect(...)` は、その `Result` に対して、

* 成功なら中身を取り出す
* 失敗なら指定メッセージで停止する

ための便利な書き方です。

---

# Rust文法として特に大事な点

ここからは、このコードを読むために必要な **Rust 文法のポイント** を JavaScript と比べながら整理します。

---

## 1. 文の終わりに `;` を付ける

Rust では多くの文の末尾に `;` が付きます。

```rust
mod downloader;
mod html_query;
```

JavaScript でも `;` を付けられますが、省略されることも多いです。
Rust では JavaScript より **きっちり付ける** 印象です。

---

## 2. `::` は Rust の名前空間アクセス

Rust:

```rust
html_query::collect_images
tauri::Builder::default()
```

JavaScript:

```javascript
html_query.collect_images
Tauri.Builder.default()
```

と考えると分かりやすいです。

ただし Rust の `::` は、オブジェクトのプロパティアクセスというより、
**モジュールや型の所属をたどる記法**です。

---

## 3. `.` はメソッド呼び出し

Rust でも `.` を使います。

```rust
.plugin(...)
.invoke_handler(...)
.run(...)
.expect(...)
```

これは JavaScript とかなり似ています。

JavaScript:

```javascript
obj.method()
```

Rust:

```rust
obj.method()
```

ここは直感的に理解しやすいです。

---

## 4. `!` はマクロ

Rust:

```rust
tauri::generate_handler![...]
tauri::generate_context!()
```

JavaScript にはほぼ直接対応するものがありません。

初心者のうちは、

**`!` が付いていたら「特別な仕組み」**

と思って大丈夫です。

このコードでは、

* `generate_handler!`
* `generate_context!`

がそれです。

---

## 5. `pub` は外部公開

Rust:

```rust
pub fn run()
```

JavaScript:

```javascript
export function run()
```

に近いです。

---

## 6. `fn` は関数定義

Rust:

```rust
fn run() { }
```

JavaScript:

```javascript
function run() { }
```

です。

---

## 7. コメントは `//`

Rust も JavaScript も同じく `//` で1行コメントが書けます。

```rust
// コメント
```

これは JavaScript と同じです。

---

# このコードの流れを超やさしく言うと

このプログラムは、次の順番で動いています。

まず、

```rust
mod downloader;
mod html_query;
```

で、別ファイルに書いた機能を読み込めるようにします。

次に、

```rust
pub fn run() {
```

で、アプリ起動用の関数を定義します。

その中で、

```rust
tauri::Builder::default()
```

で Tauri の設定作りを始めます。

そして、

```rust
.plugin(tauri_plugin_opener::init())
```

でプラグインを追加し、

```rust
.invoke_handler(tauri::generate_handler![
    html_query::collect_images,
    downloader::download
])
```

で、JavaScript 側から呼べる Rust 関数を登録します。

最後に、

```rust
.run(tauri::generate_context!())
.expect("error while running tauri application");
```

でアプリを起動し、失敗したらエラーメッセージを出します。

---

# JavaScript初心者がつまずきやすい点

このコードで特につまずきやすいのは、たぶん次の4つです。

## `mod`

これは `import` に近いものです。

## `pub`

これは `export` に近いものです。

## `::`

これは JavaScript の `.` に少し似ていますが、
「モジュールや型の中にあるもの」を表します。

## `!`

これは関数ではなく **マクロ** です。
Rust の独特な仕組みです。

---

# 一番シンプルにまとめると

このコードは、JavaScriptで言えば次のような役割です。

* 別ファイルの機能を読み込む
* アプリの設定を組み立てる
* フロントエンドから呼ぶ関数を登録する
* アプリを起動する

Rust 文法としては、

* `mod` = モジュール宣言
* `pub` = 外部公開
* `fn` = 関数定義
* `::` = モジュールや型の中の要素を指す
* `!` = マクロ
* `.xxx()` = メソッド呼び出し

を押さえると読みやすくなります。
