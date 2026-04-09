# html_query.rs の解説

このコードは、**HTMLドキュメントから画像URLを抽出する**ための Rust コードです。

もちろんです。
この `html_query.rs` は、**指定したURLのHTMLを取得して、ページ内の`img`タグから画像URLを集める処理**です。

Tauri では、この関数をフロントエンドの JavaScript から呼べるようにしています。

まずは全体の役割を一言でいうと、この関数は次の流れで動きます。

1. URL文字列を受け取る
2. そのURLのHTMLをダウンロードする
3. HTMLの中から`img`要素を探す
4. `src`属性を取り出す
5. 相対URLなら絶対URLに直す
6. 重複を除いて配列で返す

---

## まずコード全体のイメージ

JavaScript風にかなりざっくり書くと、こういう処理です。

```javascript
async function collectImages(url) {
  const response = await fetch(url);
  const body = await response.text();

  const doc = parseHTML(body);
  const imgs = doc.querySelectorAll("img");

  const seen = new Set();
  const images = [];

  for (const img of imgs) {
    const src = img.getAttribute("src");
    if (!src) continue;

    const resolved = toAbsoluteUrl(url, src);

    if (!seen.has(resolved)) {
      seen.add(resolved);
      images.push(resolved);
    }
  }

  return images;
}
```

Rust のコードは、これを **より厳密に、安全に書いている** と思うと分かりやすいです。

---

# 1. `use` 文

```rust
use std::collections::HashSet;
use scraper::{Html, Selector};
```

これは、必要な機能を使えるようにする宣言です。

### JavaScriptでたとえると

こんな感じです。

```javascript
import { Html, Selector } from "scraper";
```

ただし Rust の `use` は、JavaScript の `import` とかなり似ていますが、少し感覚が違います。
Rust では「この長い名前を、ここでは短く使えるようにする」という意味合いも強いです。

---

## `use std::collections::HashSet;`

これは、重複チェックのための `HashSet` を使う宣言です。

JavaScript の `Set` にかなり近いです。

### 対比

Rust:

```rust
HashSet
```

JavaScript:

```javascript
Set
```

---

## `use scraper::{Html, Selector};`

これは `scraper` ライブラリの中から `Html` と `Selector` を使う、という意味です。

### Rustの `{...}` の意味

ここは JavaScript の分割インポートに少し似ています。

Rust:

```rust
use scraper::{Html, Selector};
```

JavaScript:

```javascript
import { Html, Selector } from "scraper";
```

かなり似ています。

---

# 2. 関数定義

```rust
#[tauri::command]
pub async fn collect_images(url: String) -> Result<Vec<String>, String> {
```

ここは Rust の文法がたくさん詰まっています。
1つずつ見ていきます。

---

## `#[tauri::command]`

これは属性です。
この関数を **Tauri のコマンドとしてフロントエンドから呼べるようにする** ための指定です。

JavaScript には完全対応する文法はありませんが、感覚的には、

* 「この関数は普通の関数ではなく、Tauri から呼び出される特別な関数」
* 「公開APIに登録するための印」

のようなものです。

フロントエンド側では、たとえば `invoke("collect_images", { url })` のように呼ぶための準備です。

---

## `pub`

```rust
pub
```

これは外部公開です。
他の場所から使えるようにする印です。

### JavaScriptでたとえると

```javascript
export
```

に近いです。

---

## `async fn`

```rust
async fn
```

これは非同期関数です。

### JavaScriptとの対比

Rust:

```rust
async fn collect_images(...) { ... }
```

JavaScript:

```javascript
async function collectImages(...) { ... }
```

かなり似ています。

---

## `collect_images(url: String)`

これは引数付きの関数です。

### JavaScriptとの対比

Rust:

```rust
(url: String)
```

JavaScript:

```javascript
(url)
```

JavaScript では型を書きませんが、Rust では **引数の型を必ず書く** のが基本です。

つまり、

* `url` という名前の引数
* 型は `String`

という意味です。

---

## `String`

Rust の `String` は、文字列を表す型です。

JavaScript で言えば普通の文字列です。

```javascript
"hello"
```

に相当します。

ただし Rust では、文字列にもいくつか種類があるので、JavaScript より厳密です。
この場面では「可変長の普通の文字列」と思って大丈夫です。

---

## `-> Result<Vec<String>, String>`

ここが Rust らしい重要ポイントです。

この関数は、成功か失敗かを返します。

### 意味

* 成功したら `Vec<String>`
* 失敗したら `String`

を返す、という意味です。

### JavaScriptでたとえると

JavaScript なら、多くの場合はこんな感じです。

```javascript
return images;
// あるいは
throw new Error("URLが開けません");
```

Rust では、例外を好き勝手に投げるのではなく、
**成功と失敗を `Result` という型で明示する** ことが多いです。

---

## `Vec<String>`

`Vec` は Rust の可変長配列です。
JavaScript の配列 `[]` に近いです。

### 対比

Rust:

```rust
Vec<String>
```

JavaScript:

```javascript
string[]
```

あるいは単に

```javascript
["a", "b", "c"]
```

のような配列です。

つまりこの関数は、成功すると **文字列の配列** を返します。
ここでは画像URLの一覧です。

---

# 3. URLからHTMLを取得

```rust
let response = match reqwest::get(&url).await {
    Ok(response) => response,
    Err(_) => return Err("URLが開けません".to_string()),
};
```

ここも重要です。
非同期通信と、Rust のエラー処理が出てきます。

---

## `let response = ...`

`let` は変数宣言です。

### JavaScriptとの対比

Rust:

```rust
let response = ...
```

JavaScript:

```javascript
const response = ...
```

に近いです。

ただし Rust の `let` は、必ずしも `const` と同じではありません。
Rust では **基本は変更不可** なので、感覚としては `const` にかなり近いです。

---

## `reqwest::get(&url).await`

これはURLにHTTP GETリクエストを送っています。

### 分解

* `reqwest::get(...)`

  * HTTP GET
* `&url`

  * `url` を参照で渡す
* `.await`

  * 非同期処理の完了を待つ

---

## `&url` の意味

Rust の `&` は「参照」です。

JavaScript にはほぼこの文法はありません。
JavaScript では、ただ `url` を渡します。

Rust は、値をコピーするのか、借りるのか、所有権を渡すのかを厳密に扱います。
ここでは「`url` 本体を渡すのではなく、参照だけ渡す」と思えば十分です。

初心者向けには、

**`&url` は「url を見るだけで使う」書き方**

くらいでOKです。

---

## `.await`

これは JavaScript とかなり似ています。

Rust:

```rust
reqwest::get(&url).await
```

JavaScript:

```javascript
await fetch(url)
```

です。

---

## `match ... { ... }`

ここが Rust の大事な文法です。

```rust
match reqwest::get(&url).await {
    Ok(response) => response,
    Err(_) => return Err("URLが開けません".to_string()),
}
```

`match` は、値のパターンごとに処理を分ける構文です。

JavaScript で近いものを無理に書くと、

```javascript
const result = await something();
if (result is success) {
  ...
} else {
  ...
}
```

のような感じです。

ただし Rust では、単なる `if` よりもっと強力です。

---

## `Ok(response) => response`

これは「成功した場合」です。

`reqwest::get(...).await` の結果が成功なら、その中の `response` を取り出します。

### JavaScriptの感覚

```javascript
if (success) {
  return response;
}
```

に近いです。

---

## `Err(_) => return Err(...)`

これは失敗した場合です。

### `_` の意味

`_` は「値は受け取るけれど使わない」という意味です。

JavaScript なら、

```javascript
catch (e) {
  return error;
}
```

で `e` を使わない感じに近いです。

---

## `"URLが開けません".to_string()`

これは文字列リテラルを `String` 型に変換しています。

Rust では `"..."` が必ずしも `String` そのものではないので、
必要に応じて `.to_string()` で変換します。

JavaScript では気にしませんが、Rust では型を合わせる必要があります。

---

# 4. レスポンス本文を取り出す

```rust
let body = match response.text().await {
    Ok(body) => body,
    Err(_) => return Err("URLから取得したデータが不正".to_string()),
};
```

これはさっきとほぼ同じパターンです。

### やっていること

* HTTPレスポンスの本文を文字列として読む
* 成功したら `body` に入れる
* 失敗したらエラーを返す

### JavaScriptでたとえると

```javascript
const body = await response.text();
```

に近いです。
ただし Rust では失敗の可能性をきちんと `match` で処理しています。

---

# 5. `img`タグを探すためのセレクタを準備

```rust
let selector = match Selector::parse("img") {
    Ok(selector) => selector,
    Err(_) => return Err("セレクタ指定の間違い".to_string()),
};
```

これは CSS セレクタ `"img"` を解析しています。

JavaScript なら、感覚的にはこうです。

```javascript
const selector = "img";
```

ただし Rust の `scraper` ライブラリでは、
CSS セレクタ文字列をそのまま使うのではなく、あらかじめ `Selector` 型に変換します。

---

## `Selector::parse("img")`

これは、

* `"img"` という文字列を
* CSSセレクタとして解析して
* 使える形にする

という意味です。

JavaScript の `querySelectorAll("img")` の `"img"` を、
先に準備している感じです。

---

# 6. 基準URLを解析

```rust
let base_url = reqwest::Url::parse(&url).ok();
```

これは相対URLを絶対URLに直すために使う基準URLを作っています。

たとえばページURLが

```text
https://example.com/news/index.html
```

で、画像URLが

```text
images/photo.jpg
```

なら、これだけでは不完全です。
基準URLと結合して

```text
https://example.com/news/images/photo.jpg
```

に直す必要があります。

---

## `.ok()`

ここは Rust らしいです。

`parse(&url)` は成功か失敗かを持った値を返します。
`.ok()` を使うと、それを `Option` に変えます。

ざっくり言うと、

* 成功したら `Some(...)`
* 失敗したら `None`

になります。

### JavaScriptとの感覚差

JavaScript では失敗したら `null` や例外になることが多いですが、
Rust では `Option` という型で「ある／ない」をはっきり表します。

---

# 7. HTMLを解析

```rust
let document = Html::parse_document(&body);
let mut seen = HashSet::new(); // 重複チェック用のセット
let mut images = Vec::new(); // 画像URLのリスト
```

---

## `Html::parse_document(&body)`

HTML文字列を解析して、検索できる形にします。

JavaScript なら DOMParser みたいなものを思うと近いです。

```javascript
const document = parseHTML(body);
```

の感覚です。

---

## `let mut seen = HashSet::new();`

ここで重複チェック用の集合を作っています。

### `mut` の意味

Rust の変数は、基本は変更不可です。
変更したいときだけ `mut` を付けます。

Rust:

```rust
let mut seen = ...
```

JavaScript:

```javascript
const seen = new Set();
```

JavaScript では `const` でも中身は変更できますが、Rust では
「変数そのものが変更される可能性」を明示します。

初心者向けには、

**`mut` は「あとで中身を変えるので、変更可能にします」という印**

と思えば大丈夫です。

---

## `HashSet::new()`

空の `Set` を作っています。

JavaScript なら、

```javascript
new Set()
```

です。

---

## `let mut images = Vec::new();`

空の配列を作っています。

JavaScript なら、

```javascript
const images = [];
```

に近いです。

---

# 8. `img`要素を順番に処理

```rust
for element in document.select(&selector) {
```

これは `img` 要素を1つずつ取り出して処理するループです。

### JavaScriptとの対比

Rust:

```rust
for element in document.select(&selector) {
```

JavaScript:

```javascript
for (const element of document.querySelectorAll("img")) {
```

かなり近いです。

---

## `document.select(&selector)`

これはセレクタに一致する要素一覧を取っています。

JavaScript なら、

```javascript
document.querySelectorAll("img")
```

の感覚です。

---

# 9. `src`属性を取り出す

```rust
let Some(src) = element.value().attr("src") else {
    continue;
};
```

ここは Rust 初心者がかなり引っかかりやすいところです。
でも大事です。

---

## 何をしているのか

`img` タグから `src` 属性を取り出しています。
もし `src` がなければ、その要素はスキップします。

JavaScript ならこうです。

```javascript
const src = element.getAttribute("src");
if (src == null) {
  continue;
}
```

---

## `Option` 型

`attr("src")` は、必ず値があるとは限りません。
だから Rust では、

* 値がある → `Some(src)`
* 値がない → `None`

という `Option` 型で返します。

---

## `let Some(src) = ... else { ... };`

これは
**「もし `Some(src)` なら中身を取り出す。そうでなければ else を実行する」**
という意味です。

かなり最近の Rust らしい書き方です。

JavaScript で同じ意味なら、

```javascript
const src = element.getAttribute("src");
if (src === null) {
  continue;
}
```

です。

---

# 10. 空文字チェック

```rust
let src = src.trim();
if src.is_empty() {
    continue;
}
```

ここは比較的分かりやすいです。

### やっていること

* 前後の空白を削除
* 空文字ならスキップ

### JavaScriptとの対比

Rust:

```rust
let src = src.trim();
if src.is_empty() {
    continue;
}
```

JavaScript:

```javascript
const src2 = src.trim();
if (src2.length === 0) {
  continue;
}
```

---

## `is_empty()`

Rust では空文字判定に `is_empty()` をよく使います。

JavaScript なら `str.length === 0` に近いです。

---

# 11. 絶対URLに変換

```rust
let resolved = match &base_url {
    Some(base) => base
        .join(src).map(|u| u.to_string())
        .unwrap_or_else(|_| src.to_string()),
    None => src.to_string(),
};
```

ここは少し難しいですが、やっていることはシンプルです。

### やりたいこと

* `src` が相対URLなら、基準URLと結合して絶対URLにする
* 失敗したら元の `src` を使う
* 基準URLがなければ元の `src` を使う

---

## `match &base_url`

`base_url` は `Option` です。

* 値あり → `Some(base)`
* 値なし → `None`

で分けています。

JavaScript なら、

```javascript
if (baseUrl != null) {
  ...
} else {
  ...
}
```

に近いです。

---

## `Some(base) => ...`

基準URLがある場合です。

---

## `base.join(src)`

これは URL を結合しています。

たとえば、

* base: `https://example.com/a/`
* src: `img.png`

なら

* `https://example.com/a/img.png`

になります。

JavaScript なら `new URL(src, base)` に近いです。

---

## `.map(|u| u.to_string())`

ここも Rust らしいです。

成功したURLを文字列に変換しています。

### `|u| ...` は何か

これはクロージャです。
JavaScript のアロー関数にかなり近いです。

Rust:

```rust
|u| u.to_string()
```

JavaScript:

```javascript
u => u.toString()
```

です。

---

## `.unwrap_or_else(|_| src.to_string())`

これも大事です。

意味は、

* 成功したらその値を使う
* 失敗したら `src.to_string()` を使う

です。

JavaScript で雑に書くなら、

```javascript
try {
  return joined.toString();
} catch {
  return String(src);
}
```

のような感覚です。

---

## `None => src.to_string()`

基準URLがない場合は、元の `src` を文字列にして使います。

---

# 12. 重複チェックして追加

```rust
if seen.insert(resolved.clone()) {
    images.push(resolved);
}
```

ここはとても実用的です。

### やっていること

* `resolved` を `seen` に入れる
* もし初めて出てきたURLなら `images` にも追加する
* すでに存在していれば追加しない

---

## `seen.insert(...)`

`HashSet` の `insert` は、JavaScript の `Set.prototype.add()` に似ています。
ただし Rust では、**追加できたかどうかを真偽値で返す** のが便利です。

* 新しく入った → `true`
* すでにあった → `false`

JavaScript なら普通はこう書きます。

```javascript
if (!seen.has(resolved)) {
  seen.add(resolved);
  images.push(resolved);
}
```

Rust ではそれを少し短く書けます。

---

## `resolved.clone()`

ここも Rust 特有です。

`resolved` を `seen` に入れたあと、さらに `images.push(resolved)` にも使いたいので、
1つ複製を作っています。

JavaScript では文字列は気軽に再利用できますが、Rust では所有権のルールがあるため、
必要に応じて `clone()` します。

初心者向けには、

**`clone()` は「値をコピーしてもう1つ作る」**

と思って大丈夫です。

---

# 13. 結果を返す

```rust
Ok(images)
```

これは成功結果として `images` を返しています。

### JavaScriptでたとえると

```javascript
return images;
```

です。

ただし Rust では、この関数の返り値が `Result<..., ...>` なので、
成功を表す `Ok(...)` で包みます。

---

# JavaScript初心者が特につまずくRust文法まとめ

このコードで大事なものだけ整理すると、次の通りです。

---

## `use`

必要な型や機能を使えるようにする。
JavaScript の `import` に近いです。

---

## `#[tauri::command]`

Tauri から呼び出せる関数にするための属性です。
JavaScript の普通の文法には直接対応なしです。

---

## `pub fn`

公開関数を定義します。

Rust:

```rust
pub fn test() {}
```

JavaScript:

```javascript
export function test() {}
```

---

## `async fn`

非同期関数です。
JavaScript の `async function` とかなり似ています。

---

## `url: String`

引数名と型をセットで書きます。
JavaScript は型を書きませんが、Rust は書きます。

---

## `Result<Vec<String>, String>`

成功時と失敗時の型を明示しています。

* 成功 → 文字列配列
* 失敗 → エラーメッセージ文字列

---

## `match`

値の状態ごとに分岐する構文です。
`if / else` より強力です。

---

## `Some / None`

「値がある / ない」を表します。
JavaScript の `null` や `undefined` に近いですが、Rust ではもっと厳密です。

---

## `let mut`

変更可能な変数です。
`mut` がないと基本的に変更できません。

---

## `Vec`

配列のようなものです。
JavaScript の `[]` に近いです。

---

## `HashSet`

重複しない集合です。
JavaScript の `Set` に近いです。

---

## `|u| ...`

クロージャです。
JavaScript の `u => ...` に近いです。

---

## `clone()`

値を複製します。
Rust の所有権ルールのためによく出てきます。

---

# この関数をJavaScriptでかなり近い形にすると

理解しやすいように、なるべく対応させて書くとこうなります。

```javascript
async function collectImages(url) {
  let response;
  try {
    response = await fetch(url);
  } catch {
    throw new Error("URLが開けません");
  }

  let body;
  try {
    body = await response.text();
  } catch {
    throw new Error("URLから取得したデータが不正");
  }

  const selector = "img";
  const baseUrl = safeParseUrl(url);

  const document = parseHTML(body);
  const seen = new Set();
  const images = [];

  for (const element of document.querySelectorAll(selector)) {
    const src0 = element.getAttribute("src");
    if (src0 == null) continue;

    const src = src0.trim();
    if (src.length === 0) continue;

    let resolved;
    if (baseUrl != null) {
      resolved = joinUrl(baseUrl, src) ?? src;
    } else {
      resolved = src;
    }

    if (!seen.has(resolved)) {
      seen.add(resolved);
      images.push(resolved);
    }
  }

  return images;
}
```

---

# 一番大事な読み方

このコードを読むときは、次の対応を頭に入れるとかなり楽になります。

* `Vec<String>` → 文字列配列
* `HashSet` → `Set`
* `Option` → 値があるかないか
* `Result` → 成功か失敗か
* `match` → 状態ごとの分岐
* `async/await` → JavaScript とほぼ同じ感覚
* `#[tauri::command]` → Tauri から呼ぶための目印

---

# このコードの実務的なポイント

この関数はただ `img` タグを集めるだけではなく、ちゃんと次の点まで考えています。

* 通信エラー時に分かりやすいエラーを返す
* `src` がない画像を無視する
* 空の `src` を無視する
* 相対URLを絶対URLに変換する
* 重複URLを除外する

つまり、**現実のHTMLを扱うための最低限の頑丈さがある** コードです。

