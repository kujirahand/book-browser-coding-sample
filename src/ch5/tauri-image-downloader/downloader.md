# downloader.rs の解説

[このコード](src-tauri/src/downloader.rs) は、**画像のダウンロード処理**を行う Rust コードです。

この `downloader.rs` は、**画像URLの一覧を受け取って、画像をダウンロードフォルダに保存する処理**です。

前の `html_query.rs` が「画像URLを集める係」なら、こちらは
**「そのURLを実際に保存する係」** です。

JavaScript でたとえると、だいたい次のような役割です。

* `download(urls)`
  → URL配列を受け取る
* 1件ずつ `fetch` する
* バイト列を取り出す
* ローカルファイルとして保存する
* 保存できたファイルパスの配列を返す

---

# まず全体像

このファイルには、主に4つの関数があります。

1. `download`

   * 画像URL一覧をダウンロードするメイン関数
2. `sanitize_url_for_dir`

   * URLをフォルダ名に使える文字列へ変換する
3. `parent_url_string`

   * URLの親URLを取り出す
4. `strip_http_scheme`

   * `http://` や `https://` を削る

---

# JavaScriptでざっくり書くとこういう処理

まずイメージをつかみやすいように、かなり雑に JavaScript 風にすると、こうです。

```javascript
async function download(urls) {
  const downloaded = [];
  const downloadRoot = getDownloadDir();
  if (!downloadRoot) {
    throw new Error("フォルダ取得失敗");
  }

  for (const url of urls) {
    const parent = parentUrlString(url);
    const baseDirName = sanitizeUrlForDir(parent);
    const saveDir = joinPath(downloadRoot, baseDirName);

    createDirIfNeeded(saveDir);

    const filename =
      url.split("/").pop()?.split("?")[0] || "image.jpg";
    const path = joinPath(saveDir, filename);

    let response;
    try {
      response = await fetch(url);
    } catch {
      continue;
    }

    let bytes;
    try {
      bytes = await response.arrayBuffer();
    } catch {
      continue;
    }

    if (writeFile(path, bytes)) {
      downloaded.push(path);
    }
  }

  if (downloaded.length === 0) {
    throw new Error("画像のダウンロードに失敗しました");
  }
  return downloaded;
}
```

実際の Rust は、これをもっと厳密に、型安全に書いています。

---

# コードを順番に見ていきます

---

## `#[tauri::command]`

```rust
#[tauri::command]
```

これは前回も出てきましたが、
**この関数を Tauri のフロントエンドから呼べるようにするための印**です。

JavaScript には同じ文法はありません。
感覚としては、

* 「この関数は普通の内部関数ではなく、Tauri API として公開する」
* `invoke("download", { urls })` で呼べるようにする

という意味です。

---

## `pub async fn download(urls: Vec<String>) -> Result<Vec<String>, String>`

```rust
pub async fn download(urls: Vec<String>) -> Result<Vec<String>, String> {
```

ここは Rust 文法がたくさん詰まっています。

### 分解すると

* `pub`

  * 外から使える
* `async`

  * 非同期関数
* `fn`

  * 関数定義
* `download`

  * 関数名
* `urls: Vec<String>`

  * 引数 `urls` は文字列配列
* `-> Result<Vec<String>, String>`

  * 成功なら文字列配列、失敗ならエラーメッセージ文字列

### JavaScript に近づけると

```javascript
export async function download(urls) {
  // 成功時は string[]
  // 失敗時は Error
}
```

という感覚です。

---

## `Vec<String>`

```rust
urls: Vec<String>
```

これは **文字列の配列** です。

JavaScript なら

```javascript
urls
```

が普通の配列で、中身が文字列という感じです。

たとえば

```javascript
[
  "https://example.com/a.jpg",
  "https://example.com/b.png"
]
```

のようなものです。

---

## `Result<Vec<String>, String>`

これは Rust らしい書き方です。

意味は、

* 成功したら `Vec<String>`

  * 保存できたファイルパスの配列
* 失敗したら `String`

  * エラーメッセージ

です。

JavaScript なら普通は

* 成功時 `return [...]`
* 失敗時 `throw new Error(...)`

にすることが多いですが、Rust は `Result` で明示します。

---

# `let mut downloaded = Vec::new();`

```rust
let mut downloaded = Vec::new();
```

これは保存に成功したファイル一覧を入れるための空配列です。

### JavaScriptなら

```javascript
const downloaded = [];
```

に近いです。

### `let`

Rust の変数宣言です。

### `mut`

ここが大事です。
Rust では変数は基本的に変更不可です。変更したいときだけ `mut` を付けます。

この `downloaded` にはあとで `push` するので、`mut` が必要です。

### `Vec::new()`

空の配列を作っています。

---

# ダウンロード先フォルダを決める部分

```rust
let download_root = dirs::download_dir().ok_or("フォルダ取得失敗")?;
```

これは少し難しそうに見えますが、意味はシンプルです。

**OS の「ダウンロード」フォルダを取得する**
という処理です。

たとえば macOS や Windows の「Downloads」フォルダです。

---

## JavaScriptでたとえると

JavaScript だとブラウザではこういうことは普通できませんが、Node.js 的な気分で書くと

```javascript
const downloadRoot = getDownloadDir();
if (!downloadRoot) {
  throw new Error("フォルダ取得失敗");
}
```

みたいな感じです。

---

## `dirs::download_dir()`

これは「ダウンロードフォルダを返す関数」です。

ただし必ず成功するとは限らないので、返り値は `Option` です。

つまり、

* 取得できた → `Some(path)`
* 取得できなかった → `None`

です。

---

## `.ok_or("フォルダ取得失敗")`

ここが Rust の便利な書き方です。

`Option` を `Result` に変換しています。

意味としては、

* `Some(x)` なら `Ok(x)`
* `None` なら `Err("フォルダ取得失敗")`

です。

### JavaScript に近い感覚

```javascript
if (downloadRoot == null) {
  throw new Error("フォルダ取得失敗");
}
```

です。

---

## `?`

```rust
...?
```

これは Rust で非常によく出る記号です。

意味は、

* 成功なら中身を取り出して続行
* 失敗ならその場で関数から `Err(...)` を返して終わる

です。

### JavaScriptの感覚

かなり雑にいうと、

```javascript
const value = something();
if (isError(value)) return value;
```

を短く書いている感じです。

この `?` は Rust を読む上でかなり重要です。

---

# URL一覧を順番に処理する

```rust
for url in urls {
```

これは `urls` の中身を1件ずつ取り出すループです。

### JavaScriptなら

```javascript
for (const url of urls) {
```

です。

かなり近いです。

---

## Rustの `for url in urls`

JavaScript と違って、Rust では「値を借りるのか、所有権ごと受け取るのか」が重要です。

ここでは `urls` の各要素を順番に受け取っています。
初心者のうちは、まず

**「配列の中を順番に回している」**

と理解すれば十分です。

---

# 親URLを取り出す

```rust
let parent = parent_url_string(&url);
```

これは画像URLから「親URL」を作っています。

たとえば

```text
https://example.com/news/img/photo.jpg?x=1
```

なら、親URLはだいたい

```text
https://example.com/news/img/
```

のようなものになります。

これを使って、保存先フォルダ名を決めています。

---

## `&url`

ここは Rust 特有です。
`&` は参照です。

JavaScript では普通に `url` を渡しますが、Rust では

* 値を渡す
* 参照だけ渡す

を区別します。

ここでは「文字列そのものを移動せず、参照だけ渡す」という意味です。

---

# URLをフォルダ名に変換する

```rust
let base_dir_name = sanitize_url_for_dir(&parent);
```

これは URL を、そのままではフォルダ名にしづらいので、
安全な文字列に変換しています。

たとえば

```text
https://example.com/news/
```

が

```text
example_com_news_
```

のような文字列になります。

---

# 保存先フォルダを作る

```rust
let save_dir = download_root.join(base_dir_name);
```

これはパス結合です。

たとえば

* `download_root` = `/Users/me/Downloads`
* `base_dir_name` = `example_com_news_`

なら

* `/Users/me/Downloads/example_com_news_`

になります。

### JavaScriptなら

Node.js の `path.join(...)` に近いです。

---

## `.join(...)`

Rust の `PathBuf` にあるメソッドです。
JavaScript の文字列連結より安全です。

---

# フォルダがなければ作成

```rust
std::fs::create_dir_all(&save_dir).map_err(|_| "フォルダ作成失敗")?;
```

これも Rust らしい書き方です。

意味は、

* `save_dir` フォルダを作る
* 途中の親フォルダも必要なら全部作る
* 失敗したら `"フォルダ作成失敗"` を返して関数終了

です。

---

## JavaScriptに近い形

```javascript
try {
  mkdir(saveDir, { recursive: true });
} catch {
  throw new Error("フォルダ作成失敗");
}
```

のような感じです。

---

## `create_dir_all`

`mkdir -p` 的な処理です。
単なる1個のフォルダだけでなく、必要な親フォルダもまとめて作れます。

---

## `.map_err(|_| "フォルダ作成失敗")`

これも大事です。

元々のエラー型を、自分が返したいエラーメッセージに変換しています。

### `|_| ...`

これはクロージャです。
JavaScript のアロー関数に近いです。

Rust:

```rust
|_| "フォルダ作成失敗"
```

JavaScript:

```javascript
_ => "フォルダ作成失敗"
```

です。

### `_`

エラーの中身自体は使わない、という意味です。

---

## `?`

最後の `?` で、失敗ならそのまま関数から抜けます。

---

# ファイル名を決める

```rust
let filename = url
    .split('/').last().unwrap_or("image.jpg")
    .split('?').next().unwrap_or("image.jpg");
```

ここは一見長いですが、やっていることは簡単です。

たとえば URL が

```text
https://example.com/img/photo.jpg?size=large
```

だったら、ファイル名として

```text
photo.jpg
```

を取り出したい、という処理です。

---

## JavaScriptなら

```javascript
const filename =
  url.split("/").pop()?.split("?")[0] || "image.jpg";
```

にかなり近いです。

---

## `.split('/')`

JavaScript と同じ感覚です。

Rust:

```rust
url.split('/')
```

JavaScript:

```javascript
url.split("/")
```

---

## `.last()`

分割した最後の要素を取ります。

JavaScript なら

```javascript
arr[arr.length - 1]
```

や `.pop()` 的な感覚です。

ただし Rust の `last()` は元の配列を壊しません。

---

## `.unwrap_or("image.jpg")`

ここもよく出ます。

意味は、

* 値があればそれを使う
* なければ `"image.jpg"` を使う

です。

JavaScript なら

```javascript
value || "image.jpg"
```

に少し似ていますが、Rust は `Option` を明示的に扱います。

---

## `.split('?').next()`

クエリ文字列を消しています。

たとえば

```text
photo.jpg?size=large
```

を

```text
photo.jpg
```

にします。

`.next()` は最初の要素を取るので、JavaScript で言えば `[0]` っぽいです。

---

# 保存パスを作る

```rust
let path = save_dir.join(filename);
```

フォルダとファイル名をつないで、最終的な保存先パスを作っています。

たとえば

```text
/Users/me/Downloads/example_com_news_/photo.jpg
```

のような感じです。

---

# ダウンロードする

```rust
let response = match reqwest::get(&url).await {
    Ok(response) => response,
    Err(_) => continue,
};
```

これは前の `collect_images` にかなり似ています。

意味は、

* URLにアクセスする
* 成功したら `response`
* 失敗したらそのURLはあきらめて次へ

です。

---

## JavaScriptなら

```javascript
let response;
try {
  response = await fetch(url);
} catch {
  continue;
}
```

です。

---

## `continue`

これはループの現在の回を打ち切って、次の要素へ進む命令です。

JavaScript の `continue` と同じです。

---

## ここでの設計ポイント

この関数は、1件の失敗で全体を止めません。
そのURLだけスキップして、次を続けます。

つまり、

* 10枚中1枚失敗
* 残り9枚成功

なら、9枚は保存します。

これは実用的です。

---

# バイト列を取り出す

```rust
let bytes = match response.bytes().await {
    Ok(bytes) => bytes,
    Err(_) => continue,
};
```

これはレスポンス本文をバイト列で取得しています。

画像は文字列ではなく生データなので、`text()` ではなく `bytes()` を使っています。

### JavaScriptなら

```javascript
let bytes;
try {
  bytes = await response.arrayBuffer();
} catch {
  continue;
}
```

に近いです。

---

# ファイルに保存する

```rust
if std::fs::write(&path, &bytes).is_ok() {
    downloaded.push(path.to_string_lossy().to_string());
}
```

ここでは、取得したバイト列をファイルに書き込んでいます。

---

## JavaScriptなら

```javascript
if (writeFile(path, bytes)) {
  downloaded.push(String(path));
}
```

のような感じです。

---

## `std::fs::write(&path, &bytes)`

指定したパスにバイト列を書き込みます。

---

## `.is_ok()`

Rust の `Result` に対して、

* 成功なら `true`
* 失敗なら `false`

を返します。

JavaScript なら try/catch して真偽値にしている感じです。

---

## `downloaded.push(...)`

これは JavaScript と同じ感覚です。

Rust:

```rust
downloaded.push(...)
```

JavaScript:

```javascript
downloaded.push(...)
```

---

## `path.to_string_lossy().to_string()`

ここは Rust っぽいです。

`path` は普通の文字列ではなく、パス型です。
それを文字列に変換しています。

### なぜ `lossy` なのか

OS のパスは、必ずしも完全なUTF-8文字列とは限りません。
そのため「多少無理やりでも文字列にする」ために `to_string_lossy()` を使います。

初心者向けには、

**「パスを表示用の文字列に変換している」**

と覚えておけば十分です。

---

# 1件も保存できなかった場合

```rust
if downloaded.is_empty() {
    Err("画像のダウンロードに失敗しました".to_string())
} else {
    Ok(downloaded)
}
```

これは最後の結果判定です。

* 1件も成功しなかった → エラー
* 1件でも成功した → 成功配列を返す

### JavaScriptなら

```javascript
if (downloaded.length === 0) {
  throw new Error("画像のダウンロードに失敗しました");
} else {
  return downloaded;
}
```

です。

---

## `is_empty()`

これは JavaScript の `array.length === 0` に近いです。

---

## `Err(...)` / `Ok(...)`

`Result` を返すので、

* 成功 → `Ok(...)`
* 失敗 → `Err(...)`

で包みます。

---

# ここから下は補助関数

---

# `sanitize_url_for_dir`

```rust
fn sanitize_url_for_dir(url: &str) -> String {
```

この関数は URL をフォルダ名用に安全な文字列へ変換します。

### JavaScriptなら

```javascript
function sanitizeUrlForDir(url) {
```

です。

---

## `fn`

Rust の関数定義です。
`pub` がないので、このファイルの内部用です。

JavaScript でいえば `export` していない関数です。

---

## `url: &str`

ここが Rust らしいです。

`&str` は「文字列スライス」です。
ざっくり言えば、文字列への参照です。

JavaScript には直接対応する概念はありません。
初心者向けには、

**「文字列を借りて読むだけ」**

と思っておけば大丈夫です。

---

## 中身

```rust
let url = strip_http_scheme(url);
```

まず `http://` や `https://` を削っています。

---

```rust
let mut sanitized: String = url.chars().map(|c| {
        if c.is_ascii_alphanumeric() { c } else { '_' }
    }).collect();
```

ここは少し難しめですが、やっていることは分かりやすいです。

**URLの文字を1文字ずつ見て、英数字ならそのまま、そうでなければ `_` に置き換える**

という処理です。

---

## JavaScriptで書くと

```javascript
let sanitized = [...url]
  .map(c => /[a-zA-Z0-9]/.test(c) ? c : "_")
  .join("");
```

にかなり近いです。

---

## `url.chars()`

文字を1文字ずつ取り出します。

---

## `.map(|c| { ... })`

`map` は JavaScript と似ています。

Rust:

```rust
.map(|c| ...)
```

JavaScript:

```javascript
.map(c => ...)
```

です。

---

## `if c.is_ascii_alphanumeric() { c } else { '_' }`

英数字ならその文字を返し、そうでなければ `_` を返します。

Rust の `if` は文ではなく**式**として使えるのが特徴です。
つまり値を返せます。

JavaScript なら三項演算子に近い感覚です。

```javascript
/[a-zA-Z0-9]/.test(c) ? c : "_"
```

---

## `.collect()`

ここも Rust 特有です。

`chars().map(...)` の結果をまとめて、最終的に `String` を作ります。

JavaScript なら `.join("")` に近い感じです。

---

## 空文字なら `"unknown"`

```rust
if sanitized.is_empty() {
    sanitized = "unknown".to_string();
}
```

変換結果が空文字だった場合の保険です。

---

# `parent_url_string`

```rust
fn parent_url_string(url: &str) -> String {
```

これは URL から親URLを作る関数です。

---

## 解析部分

```rust
let Ok(mut parsed) = reqwest::Url::parse(url) else {
    return url.to_string();
};
```

ここは最近の Rust らしい書き方です。

意味は、

* URL解析に成功したら `parsed` に入れる
* 失敗したら元の文字列をそのまま返す

です。

### JavaScriptなら

```javascript
let parsed;
try {
  parsed = new URL(url);
} catch {
  return String(url);
}
```

に近いです。

---

## `let Ok(...) = ... else { ... };`

これは
**パターンに一致したら中身を取り出し、一致しなければ else を実行する**
という構文です。

前回の `let Some(src) = ... else { ... };` と同じ系統です。

---

## `mut parsed`

あとで `parsed` を変更するので `mut` が必要です。

---

## クエリとフラグメントを消す

```rust
parsed.set_query(None);
parsed.set_fragment(None);
```

これは URL の `?query=...` や `#fragment` を削っています。

たとえば

```text
https://example.com/a/b.jpg?x=1#top
```

が

```text
https://example.com/a/b.jpg
```

になります。

---

## パス末尾を1個削る

```rust
if let Ok(mut segments) = parsed.path_segments_mut() {
    segments.pop_if_empty();
    segments.pop();
}
```

これで URL の最後のファイル名部分を削って、親ディレクトリっぽいURLにしています。

---

## `if let Ok(...) = ...`

これも Rust らしい省略記法です。

JavaScript なら

```javascript
const result = something();
if (result is ok) {
  ...
}
```

に相当します。

---

## `parsed.to_string()`

最後に URL を文字列へ戻します。

---

# `strip_http_scheme`

```rust
fn strip_http_scheme(url: &str) -> &str {
```

これは URL 文字列の先頭にある `https://` や `http://` を外すだけの関数です。

---

## 中身

```rust
url.strip_prefix("https://")
    .or_else(|| url.strip_prefix("http://"))
    .unwrap_or(url)
```

これも Rust らしい連鎖です。

意味は、

1. まず `https://` を消せるか試す
2. ダメなら `http://` を消せるか試す
3. どちらもダメなら元の `url` を返す

---

## JavaScriptなら

```javascript
return url.startsWith("https://")
  ? url.slice("https://".length)
  : url.startsWith("http://")
    ? url.slice("http://".length)
    : url;
```

です。

---

## `strip_prefix(...)`

先頭一致していればその部分を削った結果を返します。

---

## `or_else(...)`

最初がダメだったら次を試す、という意味です。

### `|| ...`

ここもクロージャです。
JavaScript の

```javascript
() => ...
```

に近いです。

---

## `unwrap_or(url)`

値があればそれを返し、なければ `url` を返します。

---

# このファイルで特に覚えたい Rust 文法

この `downloader.rs` で重要な文法だけまとめると、次のとおりです。

---

## `Vec<String>`

文字列配列。
JavaScript の `string[]` や普通の配列に近いです。

---

## `Result<T, E>`

成功か失敗かを表す型。
JavaScript なら `return` と `throw` を型として明示している感じです。

---

## `Option<T>`

値があるかないかを表す型。
JavaScript の `null` より厳密です。

---

## `?`

失敗したらその場で関数を抜ける便利記法です。

---

## `match`

成功/失敗や値の種類ごとに分岐する構文です。

---

## `if let` / `let ... else`

「特定の形なら中身を取り出す」という Rust らしい書き方です。

---

## `mut`

変更可能にする印です。

---

## `&str`

文字列参照。
「文字列を借りて読むだけ」という感覚で大丈夫です。

---

## クロージャ `|x| ...`

JavaScript のアロー関数に近いです。

Rust:

```rust
|x| x + 1
```

JavaScript:

```javascript
x => x + 1
```

---

# このコードの実務上の良い点

このコードは、初心者向けサンプルとしてもなかなか実用的です。

良い点は次の通りです。

* ダウンロードフォルダをOSに合わせて取得している
* URLごとに整理されたサブフォルダへ保存している
* 1件失敗しても全体を止めない
* 1件も成功しなければエラーを返す
* URLからクエリ文字列を除いてファイル名を決めている
* フォルダ名に使えない文字を `_` に置き換えている

---

# 注意点もあります

実用上は、少し気になる点もあります。

### 1. 同じファイル名だと上書きの可能性がある

`photo.jpg` が同名で複数あると、後のものが前を上書きするかもしれません。

### 2. HTTPステータスを見ていない

`404` や `500` でも `reqwest::get()` 自体は成功扱いになることがあります。
本格的には `response.status().is_success()` を確認した方が安全です。

### 3. 拡張子がないURLに弱い

URL末尾がファイル名らしくない場合、保存名が変になることがあります。

でも、入門サンプルとしては十分分かりやすい構成です。

---

# 一番シンプルに言うと

この `downloader.rs` は、

* 画像URLの配列を受け取る
* ダウンロードフォルダ配下に保存先を作る
* 画像を1枚ずつ保存する
* 保存できたファイルの一覧を返す

という処理です。

JavaScript と比べると、Rust では特に次の点が特徴です。

* 引数と戻り値の型を明示する
* 成功/失敗を `Result` で表す
* 値の有無を `Option` で表す
* `?` でエラー処理を簡潔に書く
* `&str` や `clone` など、所有権や参照の考え方がある
