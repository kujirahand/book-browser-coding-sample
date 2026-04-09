# src-tauri/src/csv_processing.rs の解説

[src-tauri/src/csv_processing.rs](src-tauri/src/csv_processing.rs)に関する解説です。

この `csv_processing.rs` は、**複数のCSVファイルを読み込んで、支店ごとの売上を集計する**ための Rust のコードです。

JavaScript初心者向けに、まず全体の動き、そのあとで **Rustの文法** を多めに解説します。

---

# このプログラムがやっていること

このファイルの役目は、ざっくり言うと次の通りです。

1. `Documents/demo_keiri` フォルダを探す
2. その中にある `branch_*.csv` という名前のCSVを順番に読む
3. 各CSVの **7列目の金額** を合計する
4. 各支店ごとに
   * 支店ID
   * 売上合計
   * 取引件数
     をまとめる
5. 売上が大きい順に並べて返す

つまり、JavaScript風に言えば、こういうイメージです。

```js
// イメージ
const results = csvFiles.map(file => {
  return {
    branch: 支店ID,
    total_sales: 売上合計,
    transaction_count: 件数
  };
}).sort((a, b) => b.total_sales - a.total_sales);
```

---

# まず全体の中心になる関数

中心はこの関数です。

```rs
pub fn load_branch_sales_rows() -> Result<Vec<BranchSales>, String>
```

これは、

* `BranchSales` の配列を返したい
* でも失敗するかもしれない
* 失敗したらエラーメッセージ文字列を返す

という意味です。

JavaScript初心者向けに言うと、次のような感じです。

```js
function loadBranchSalesRows() {
  // 成功したら BranchSales[] を返す
  // 失敗したら エラーメッセージ を返す
}
```

ただし Rust では、
「成功か失敗か」をあいまいにせず、**型として明示**します。

---

# Rustでよく出てくる基本文法

このコードを読むために、先に重要なRust文法を押さえます。

## 1. `let` は変数宣言

```rs
let data_dir = get_csv_dir()?;
```

JavaScriptなら:

```js
const dataDir = getCsvDir();
```

に近いです。

ただし Rust の `let` は `const` と `let` の中間みたいな感じで、
**基本は再代入できない**変数です。

---

## 2. `mut` が付くと変更できる

```rs
let mut rows = vec![];
```

これは「変更可能な変数 `rows` を作る」という意味です。

JavaScriptなら:

```js
let rows = [];
```

に近いです。

Rustでは `mut` がないと、あとから `push` したり値を変えたりできません。

---

## 3. `Vec<T>` は配列っぽいもの

```rs
Vec<BranchSales>
```

これは「`BranchSales` 型の要素を並べた可変長配列」です。

JavaScriptなら:

```js
Array<BranchSales>
```

みたいなイメージです。

`vec![]` は JavaScript の `[]` にかなり近いです。

```rs
let mut rows = vec![];
```

↓

```js
let rows = [];
```

---

## 4. `Result<成功型, 失敗型>` は成功か失敗か

```rs
Result<Vec<BranchSales>, String>
```

これは、

* 成功なら `Vec<BranchSales>`
* 失敗なら `String`

を返すという型です。

JavaScriptでは例外を `throw` することが多いですが、Rustでは
**関数の戻り値に「失敗の可能性」を含める**ことがよくあります。

イメージ:

```js
// Rustの Result に近い考え方
{ ok: true, value: [...] }
{ ok: false, error: "エラー" }
```

---

## 5. `?` は「失敗したらそのまま返す」

```rs
let data_dir = get_csv_dir()?;
```

これはRustで非常によく使う文法です。

意味は、

* `get_csv_dir()` を実行
* 成功したら中身だけ取り出して `data_dir` に入れる
* 失敗したら、この関数もそこで終了してエラーを返す

です。

JavaScriptっぽく書くと:

```js
const result = getCsvDir();
if (result.error) {
  return result.error;
}
const dataDir = result.value;
```

に近いです。

---

## 6. `&str` と `String`

Rustでは文字列に2種類よく出てきます。

### `&str`

文字列への参照です。軽いです。

```rs
fn parse_number(input: &str) -> f64
```

JavaScriptでは文字列は全部 `string` ですが、Rustでは
「借りて読むだけの文字列」と「所有している文字列」が分かれます。

### `String`

所有している文字列です。

```rs
suffix.to_string()
```

これは「`&str` を `String` に変換する」という意味です。

---

## 7. `&Path` は「パスを借りて使う」

```rs
fn is_branch_csv(path: &Path) -> bool
```

これは「ファイルパスを受け取るけど、所有権はもらわず、借りて読むだけ」という意味です。

JavaScriptではあまり意識しませんが、Rustでは
**値を所有するのか、借りるのか** が重要です。

---

## 8. `pub fn` は公開関数

```rs
pub fn load_branch_sales_rows() -> Result<Vec<BranchSales>, String>
```

* `fn` は関数定義
* `pub` は他のファイルから使えるように公開する

JavaScriptの `export function` に近いです。

```js
export function loadBranchSalesRows() {
}
```

---

# 先頭の `use` の意味

```rs
use std::fs;
use std::path::{Path, PathBuf};

use crate::BranchSales;
```

これは「必要な機能を読み込む」宣言です。

JavaScriptなら:

```js
import fs from "fs";
```

みたいなものです。

それぞれの意味はこうです。

* `std::fs`
  ファイル操作の標準ライブラリ
* `std::path::{Path, PathBuf}`
  パスを扱う型
* `crate::BranchSales`
  同じプロジェクト内で定義されている `BranchSales` 型を使う

`crate` は「このプロジェクト自身」という意味です。

---

# 定数定義

```rs
const ERR_IO: &str = "CSVの読み込みに失敗しました。";
const ERR_CSV_FORMAT: &str = "CSVの形式が不正です。";
```

これは定数です。

JavaScriptなら:

```js
const ERR_IO = "CSVの読み込みに失敗しました。";
const ERR_CSV_FORMAT = "CSVの形式が不正です。";
```

に近いです。

Rustでは型も書きます。

* `&str` は文字列参照
* `const` は変更できない定数

---

# 関数ごとに詳しく解説

---

## 1. `load_branch_sales_rows`

```rs
pub fn load_branch_sales_rows() -> Result<Vec<BranchSales>, String> {
```

この関数は「すべての支店CSVを調べて、集計結果一覧を返す」関数です。

---

### CSVフォルダを取得

```rs
let data_dir = get_csv_dir()?;
```

ここでは `get_csv_dir()` を呼んで、CSVが入っているフォルダを取得します。

`?` があるので、失敗したらそのままエラーを返して終了します。

---

### 空の配列を作る

```rs
let mut rows = vec![];
```

集計結果を入れる空の配列です。

* `let` = 変数宣言
* `mut` = 後で変更する
* `vec![]` = 空のベクタ

JavaScriptなら:

```js
let rows = [];
```

---

### フォルダの中を順番に読む

```rs
for entry in fs::read_dir(&data_dir).map_err(|_| ERR_IO.to_string())? {
```

ここは少し難しいですが、分解するとこうです。

#### `fs::read_dir(&data_dir)`

フォルダの中身を読む

#### `map_err(|_| ERR_IO.to_string())`

もし元のエラーが出たら、自分のエラーメッセージに変換する

#### `?`

失敗したらそのまま返す

### `|_|` って何？

これはクロージャです。JavaScript のアロー関数に近いです。

```rs
|_| ERR_IO.to_string()
```

JavaScriptなら:

```js
(_) => ERR_IO.toString()
```

みたいな感じです。

`_` は「引数は受け取るけど使わない」という意味です。

---

### 各ファイルのパスを取得

```rs
let path = entry
    .map_err(|_| ERR_IO.to_string())?
    .path();
```

`entry` も失敗する可能性があるので、また `map_err(...)?` を使っています。

最後の `.path()` で、そのファイルのパスを取り出します。

メソッドチェーンなので、JavaScriptの

```js
const path = entry.path();
```

っぽく見えますが、途中にエラー処理が挟まっています。

---

### 支店CSVか判定して、違えばスキップ

```rs
if !is_branch_csv(&path) {
    continue;
}
```

* `!` は否定
* `continue` はループの次へ進む

JavaScriptなら:

```js
if (!isBranchCsv(path)) {
  continue;
}
```

Rustでは `&path` として、`path` を借りて関数に渡しています。

---

### 支店IDを取り出す

```rs
let branch = branch_id_from_path(&path);
```

例えば `branch_tokyo.csv` から `tokyo` を取り出します。

---

### CSVを集計する

```rs
let (total_sales, transaction_count) = summarize_csv_file(&path)?;
```

ここは **タプルの分解代入** です。

`summarize_csv_file` は `(f64, usize)` を返します。
つまり「2つの値のセット」を返します。

JavaScriptなら:

```js
const [totalSales, transactionCount] = summarizeCsvFile(path);
```

に近いです。

Rustの `(a, b)` はタプルです。

---

### 構造体を配列に追加

```rs
rows.push(BranchSales {
    branch,
    total_sales,
    transaction_count,
});
```

これは `BranchSales` 構造体を作って `rows` に追加しています。

JavaScriptなら:

```js
rows.push({
  branch: branch,
  total_sales: total_sales,
  transaction_count: transaction_count
});
```

に近いです。

しかもRustでは、**変数名とフィールド名が同じなら省略できる**ので、

```rs
BranchSales {
    branch,
    total_sales,
    transaction_count,
}
```

は、実質こういう意味です。

```rs
BranchSales {
    branch: branch,
    total_sales: total_sales,
    transaction_count: transaction_count,
}
```

---

### 売上の大きい順にソート

```rs
rows.sort_by(|a, b| {
    b.total_sales
        .partial_cmp(&a.total_sales)
        .unwrap_or(std::cmp::Ordering::Equal)
});
```

ここは少し難所です。

JavaScriptなら本当はこう書きたいところです。

```js
rows.sort((a, b) => b.total_sales - a.total_sales);
```

でも Rust の `f64` は浮動小数点数なので、
単純比較で問題が出ることがあります。
そのため `partial_cmp` を使います。

### `|a, b| { ... }`

これはクロージャです。

JavaScriptなら:

```js
(a, b) => { ... }
```

です。

### `partial_cmp`

部分比較です。`f64` 用の比較メソッドです。

### `unwrap_or(...)`

比較できなかったときの代わりの値を使います。

JavaScriptで近い雰囲気にすると:

```js
const result = compare(a, b);
return result ?? 0;
```

という感じです。

---

### 結果が空ならエラー

```rs
if rows.is_empty() {
    return Err("支店CSVが見つかりませんでした。".to_string());
}
```

JavaScriptなら:

```js
if (rows.length === 0) {
  throw new Error("支店CSVが見つかりませんでした。");
}
```

みたいな感覚です。

Rustでは `Err(...)` を返します。

---

### 成功なら `Ok(rows)`

```rs
Ok(rows)
```

Rustの `Result` は

* 成功 → `Ok(...)`
* 失敗 → `Err(...)`

です。

---

## 2. `get_csv_dir`

```rs
fn get_csv_dir() -> Result<PathBuf, String> {
```

この関数は `Documents/demo_keiri` の実際のパスを返します。

* `fn` なので非公開関数
* `PathBuf` は「所有しているパス」
* 失敗時は文字列エラー

---

### ドキュメントフォルダを取得

```rs
let documents_dir = dirs::document_dir()
    .ok_or_else(|| "ドキュメントフォルダが見つかりません。".to_string())?;
```

ここもRustらしい書き方です。

`dirs::document_dir()` は `Option<PathBuf>` を返します。
つまり「あるかもしれないし、ないかもしれない」です。

### `Option` とは

Rustでは「値があるかないか」を

* `Some(値)`
* `None`

で表します。

JavaScriptで言えば:

* 値あり
* `null` / `undefined`

に近いです。

### `ok_or_else(...)`

`Option` を `Result` に変換しています。

* `Some(x)` なら `Ok(x)`
* `None` なら `Err(...)`

という変換です。

JavaScriptっぽく言えば:

```js
if (documentsDir == null) {
  return "ドキュメントフォルダが見つかりません。";
}
```

みたいな意味です。

### `||`

これは引数なしクロージャです。

JavaScriptなら:

```js
() => "ドキュメントフォルダが見つかりません。"
```

です。

---

### パスをつなげる

```rs
let dir = documents_dir.join("demo_keiri");
```

`join` はパス結合です。

JavaScriptの文字列連結より安全です。

```js
const dir = path.join(documentsDir, "demo_keiri");
```

みたいな感じです。

---

### フォルダかチェック

```rs
if dir.is_dir() {
    Ok(dir)
} else {
    Err("CSVフォルダが見つかりません。".to_string())
}
```

Rustでは `if` は**値を返せます**。
ここでは `Ok(dir)` か `Err(...)` を返しています。

JavaScriptだと `return` を書きたくなる場面ですが、Rustではこういう書き方が自然です。

---

## 3. `is_branch_csv`

```rs
fn is_branch_csv(path: &Path) -> bool {
```

これは「このパスが支店CSVかどうか」を判定します。
戻り値が `bool` なので、結果は `true` / `false` です。

---

### `let Some(...) = ... else { ... };`

```rs
let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
    return false;
};
```

これはRustの中でも特徴的な文法です。

意味は、

* `path.file_name().and_then(...)` の結果が `Some(name)` なら続行
* `None` なら `else` 側を実行して `false` を返す

です。

JavaScriptっぽく書くと:

```js
const name = path.fileName()?.toString();
if (name == null) {
  return false;
}
```

に近いです。

### `and_then`

`Option` の中身に対してさらに処理するメソッドです。

ここでは

* `file_name()` でファイル名を得る
* `to_str()` で文字列に変換する

をつないでいます。

---

### 小文字化

```rs
let lower = name.to_ascii_lowercase();
```

これはファイル名を小文字にしています。

JavaScriptなら:

```js
const lower = name.toLowerCase();
```

---

### 名前チェック

```rs
if !lower.starts_with("branch_") || !lower.ends_with(".csv") {
    return false;
}
true
```

これは

* `branch_` で始まるか
* `.csv` で終わるか

を確認しています。

JavaScriptなら:

```js
if (!lower.startsWith("branch_") || !lower.endsWith(".csv")) {
  return false;
}
return true;
```

最後の `true` を返しているのもRustらしいです。
**末尾の式が戻り値**になります。

---

## 4. `branch_id_from_path`

```rs
fn branch_id_from_path(path: &Path) -> String {
```

ファイル名から支店IDを作ります。

たとえば

* `branch_tokyo.csv` → `tokyo`

です。

---

### 拡張子を除いたファイル名を取る

```rs
let file_stem = path
    .file_stem()
    .and_then(|name| name.to_str())
    .unwrap_or("branch_unknown");
```

ここでは

* `file_stem()` で拡張子なしの名前を取る
* 文字列に変換する
* 失敗したら `"branch_unknown"` を使う

という流れです。

### `unwrap_or`

値があればそれを使い、なければデフォルト値を使う

JavaScriptなら:

```js
const fileStem = maybeValue ?? "branch_unknown";
```

に近いです。

---

### `_` で分割する

```rs
if let Some((_, suffix)) = file_stem.split_once('_') {
    suffix.to_string()
} else {
    file_stem.to_string()
}
```

これもRustらしい書き方です。

### `split_once('_')`

最初の `_` で2つに分割します。

たとえば:

```rs
"branch_tokyo"
```

なら

```rs
("branch", "tokyo")
```

になります。

### `if let`

「この形にマッチしたときだけ中に入る」という文法です。

JavaScriptなら:

```js
const parts = fileStem.split("_", 2);
if (parts.length === 2) {
  return parts[1];
} else {
  return fileStem;
}
```

に近いです。

### `(_, suffix)`

これはタプルの分解です。

* `_` は前半は使わない
* `suffix` に後半を入れる

という意味です。

---

## 5. `summarize_csv_file`

```rs
fn summarize_csv_file(path: &Path) -> Result<(f64, usize), String> {
```

これは1つのCSVを集計します。

戻り値は

* `f64` = 売上合計
* `usize` = 件数

のタプルです。

### `usize` とは

配列の添字や件数などに使う符号なし整数です。
JavaScriptには厳密には対応する型はありませんが、普通の数値だと思って大丈夫です。

---

### CSVリーダーの生成

```rs
let mut reader = csv::ReaderBuilder::new()
    .has_headers(true)
    .from_path(path)
    .map_err(|_| ERR_IO.to_string())?;
```

これはCSVファイルを読むための準備です。

JavaScriptでいうと、CSVライブラリを初期化している感じです。

#### `ReaderBuilder::new()`

ビルダーを作る

#### `.has_headers(true)`

1行目を見出しとして扱う

#### `.from_path(path)`

ファイルを開く

#### `.map_err(...) ?`

失敗したらエラーメッセージを変換して返す

---

### 合計と件数を初期化

```rs
let mut total_sales = 0.0;
let mut transaction_count = 0;
```

JavaScriptなら:

```js
let totalSales = 0.0;
let transactionCount = 0;
```

です。

---

### 各行を読む

```rs
for row in reader.records() {
```

CSVの各行を順番に処理しています。

JavaScriptなら:

```js
for (const row of reader.records()) {
}
```

に近いです。

---

### 行の読み取りエラー処理

```rs
let row = row.map_err(|_| ERR_CSV_FORMAT.to_string())?;
```

各行の取得も失敗するかもしれないので、ここでエラーを処理しています。

---

### 7列目を取り出す

```rs
if let Some(value) = row.get(6) {
    total_sales += parse_number(value);
    transaction_count += 1;
}
```

`row.get(6)` は 7列目の値を取り出します。
Rustでは添字は 0 から始まるので、6 は7番目の列です。

### `if let Some(value) = ...`

これもよく出る文法です。

* 値があれば `value` に入れて処理
* なければ何もしない

JavaScriptなら:

```js
const value = row[6];
if (value !== undefined) {
  totalSales += parseNumber(value);
  transactionCount += 1;
}
```

に近いです。

---

### 最後に返す

```rs
Ok((total_sales, transaction_count))
```

タプルを `Ok` に包んで返しています。

---

## 6. `parse_number`

```rs
fn parse_number(input: &str) -> f64 {
```

文字列から数値を作る関数です。

たとえば `"¥12,345"` のような文字列から、数字だけを取り出して `12345` にしたいわけです。

---

### 文字を1文字ずつ処理

```rs
let normalized: String = input
    .chars()
    .filter(|ch| ch.is_ascii_digit() || *ch == '.' || *ch == '-')
    .collect();
```

これはかなりRustらしい書き方です。

順番に見ると:

#### `.chars()`

文字列を1文字ずつに分ける

#### `.filter(...)`

条件に合う文字だけ残す

#### `.collect()`

最後にまとめて `String` にする

JavaScriptなら:

```js
const normalized = [...input]
  .filter(ch => /[0-9.-]/.test(ch))
  .join("");
```

に近いです。

### `|ch|`

クロージャの引数です。JavaScriptの

```js
(ch) =>
```

と同じです。

### `*ch == '.'`

`ch` は参照なので、`*` で中身を取り出して比較しています。
ここはRust特有です。

---

### 数値に変換

```rs
normalized.parse::<f64>().unwrap_or(0.0)
```

これは文字列を `f64` に変換しています。

### `parse::<f64>()`

「`f64` 型として解釈してね」という意味です。

JavaScriptなら:

```js
parseFloat(normalized)
```

に近いです。

### `unwrap_or(0.0)`

変換に失敗したら `0.0` を使う

JavaScriptなら:

```js
const n = parseFloat(normalized);
return Number.isNaN(n) ? 0.0 : n;
```

みたいな感じです。

---

# このプログラム全体の流れを、もっと簡単に言うと

このコードは、次の順番で動きます。

```text
load_branch_sales_rows()
  ↓
get_csv_dir() で Documents/demo_keiri を探す
  ↓
フォルダ内を1ファイルずつ見る
  ↓
is_branch_csv() で branch_*.csv か確認
  ↓
branch_id_from_path() で支店IDを作る
  ↓
summarize_csv_file() で7列目の金額を合計
  ↓
BranchSales にまとめて rows に追加
  ↓
売上順に sort
  ↓
結果を返す
```

---

# JavaScript初心者が覚えるとよいRust文法まとめ

このコードで特に重要なのは次のあたりです。

## `Result`

失敗の可能性を戻り値に含める

```rs
Result<T, E>
```

## `?`

エラーならその場で返す

```rs
let x = some_func()?;
```

## `Option`

値があるかないか

```rs
Some(value)
None
```

## `if let` / `let Some(...) = ... else`

`Some` のときだけ値を取り出す

```rs
if let Some(v) = value { ... }
```

## `Vec`

配列っぽいもの

```rs
let mut v = vec![];
v.push(x);
```

## タプル

複数の値をまとめて返す

```rs
let (a, b) = func();
```

## クロージャ

JavaScriptのアロー関数に近い

```rs
|x| x + 1
```

---

# JavaScriptとの感覚の違い

JavaScript初心者が最初に戸惑いやすい点もまとめます。

## 1. エラー処理が厳密

JavaScriptでは `throw` に頼りがちですが、Rustは `Result` を使って「失敗するかも」をはっきり書きます。

## 2. `null` / `undefined` の代わりに `Option`

Rustは「値がない」を `None` で表します。

## 3. 所有権と参照がある

`&str` や `&Path` のように、「借りて使う」ことが明確です。

## 4. 型がとてもはっきりしている

`f64`, `usize`, `String`, `PathBuf` など、何の型かをきちんと書きます。

---

# ひとことで言うと、このRustコードは何が上手いのか

このコードの良いところは次の3つです。

1. **処理を小さな関数に分けている**
   役割が分かりやすい

2. **エラー処理が丁寧**
   `Result` と `?` で安全

3. **ファイル名チェック・数値変換・集計が整理されている**
   読みやすい
