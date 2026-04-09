# TauriとChart.jsでデータ可視化アプリを作ろう

支店の売上グラフを表示するデスクトップアプリを作ります。書籍の3章で、Webアプリから支店の売り上げ情報をCSVに保存するプログラムを作ってみました。今回は、そのCSVファイルを読み込んで、支店の売り上げ情報をグラフ化して表示するデスクトップアプリをTauriで作成してみましょう。

## インストールの方法について

```sh
cd tauri-visualizer
# Tauriのライブラリをインストール
npm install
# Chart.jsをインストール
npm install chart.js
# ビルド
cd src-tauri
cargo add csv
cargo add dirs
# Tauriで実行
npm run tauri dev
```

## Rustについての説明

CSVファイルの列挙や読み取りなどの処理は、バックエンドのRust側で実装しました。

以下のプロンプトを使って、Rustの解説を行わせてみます。

```md
以下は、Tauriのバックエンド側のライブラリ「csv_processing.rs」です。JavaScript初心者にもわかりやすく、プログラムの動作を解説してください。特に、Rustの文法の解説を多く入れてください。

<プログラム>
```

Rustに関する解説は次の通りです。

### src-tauri/src/csv_processing.rs

フロントエンドから呼び出すAPIのコードです。[src-tauri/src/csv_processing.rs](src-tauri/src/csv_processing.rs)については、次のようになります。

もちろんです。
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


### src-tauri/src/lib.rs

ありがとうございます。
この `lib.rs` は、**Tauri アプリのバックエンド側の入口**です。

前回の `csv_processing.rs` が「CSVを集計する実務処理」だったのに対して、こちらの `lib.rs` は、

* モジュールを読み込む
* 集計結果を入れるデータ型を定義する
* フロントエンドから呼べるコマンドを定義する
* Tauri アプリを起動する

という、**全体の配線役**を担当しています。

JavaScript初心者向けに、まず全体像を説明してから、**Rustの文法中心**に細かく見ていきます。

---

# このファイルの役目

この `lib.rs` は、ひとことで言うと、

**「CSV集計機能をTauriのフロントエンドから呼べるようにする入口ファイル」**

です。

流れとしてはこうです。

1. `csv_processing.rs` を読み込む
2. 集計結果を表す `BranchSales` と `BranchSalesReport` を定義する
3. `load_branch_sales()` という Tauri コマンドを作る
4. フロントエンドからそのコマンドを呼べるように登録する
5. Tauri アプリを起動する

JavaScriptっぽくイメージすると、かなり大ざっぱですが次のような感じです。

```js
// イメージ
import { loadBranchSalesRows } from "./csv_processing.js";

function loadBranchSales() {
  const rows = loadBranchSalesRows();
  return { rows };
}

startTauriApp({
  commands: {
    loadBranchSales
  }
});
```

Rustではこれを、もっと厳密な型とマクロを使って書いています。

---

# コード全体

```rs
mod csv_processing; // CSV処理モジュールを利用することを宣言 --- (*1)

use crate::csv_processing::load_branch_sales_rows;
use serde::Serialize;

// 支店の売上集計結果を表す構造体 --- (*2)
#[derive(Debug, Serialize)]
pub struct BranchSales {
    pub branch: String,
    pub total_sales: f64,
    pub transaction_count: usize,
}
#[derive(Debug, Serialize)]
pub struct BranchSalesReport {
    pub rows: Vec<BranchSales>,
}

// フロントエンド側から呼び出すコマンド --- (*3)
// demo_keiri内の支店CSVを走査し、支店名と売上合計を返す。
#[tauri::command]
fn load_branch_sales() -> Result<BranchSalesReport, String> {
    let rows = load_branch_sales_rows()?;
    Ok(BranchSalesReport { rows })
}

// Tauriアプリ本体の起動設定。 --- (*4)
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![load_branch_sales])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

# まず最初に全体の意味をざっくり

このファイルは、役割ごとに4つに分かれています。

## 1. モジュールの宣言と読み込み

```rs
mod csv_processing;
use crate::csv_processing::load_branch_sales_rows;
use serde::Serialize;
```

## 2. データ型の定義

```rs
pub struct BranchSales { ... }
pub struct BranchSalesReport { ... }
```

## 3. フロントエンドから呼ぶコマンド

```rs
#[tauri::command]
fn load_branch_sales() -> Result<BranchSalesReport, String> { ... }
```

## 4. Tauriアプリの起動設定

```rs
pub fn run() { ... }
```

---

# Rust文法を中心に順番に解説

---

## 1. `mod csv_processing;`

```rs
mod csv_processing;
```

これは、**同じプロジェクト内の `csv_processing.rs` をモジュールとして使う**宣言です。

JavaScriptなら、感覚としてはこんな感じです。

```js
import "./csv_processing.js";
```

ただし Rust では、`mod` は単なる読み込みではなく、
**「この名前のモジュールがあります」**と宣言する意味が強いです。

### Rustの `mod`

* `mod csv_processing;`

  * `csv_processing.rs` というファイルをこのモジュールとして組み込む

つまり、前回の `csv_processing.rs` がこの `lib.rs` から見えるようになります。

---

## 2. `use crate::csv_processing::load_branch_sales_rows;`

```rs
use crate::csv_processing::load_branch_sales_rows;
```

これは、`csv_processing` モジュールの中にある
`load_branch_sales_rows` 関数を使えるようにする宣言です。

JavaScriptならこういう感じです。

```js
import { loadBranchSalesRows } from "./csv_processing.js";
```

### `use` とは

Rustの `use` は、他の場所にある名前を短く書けるようにするものです。

もし `use` を書かなければ、毎回こんなふうに書くことになります。

```rs
crate::csv_processing::load_branch_sales_rows()
```

`use` があると、単に

```rs
load_branch_sales_rows()
```

と書けます。

### `crate` とは

`crate` は「このプロジェクト自身」という意味です。

JavaScriptでいう「このアプリ内のモジュール」くらいの感覚で大丈夫です。

---

## 3. `use serde::Serialize;`

```rs
use serde::Serialize;
```

これは、`Serialize` という仕組みを使うための宣言です。

Tauriでは、Rustのデータをフロントエンド側へ返すときに、
**JSONに変換できること**が重要です。

そのため、`BranchSales` や `BranchSalesReport` に
`Serialize` を付けられるようにしています。

JavaScriptではオブジェクトはそのままJSONにしやすいですが、
Rustでは「この型はシリアライズ可能です」と明示する必要があります。

---

# 構造体の定義

---

## 4. `#[derive(Debug, Serialize)]`

```rs
#[derive(Debug, Serialize)]
```

これは Rust の **属性(attribute)** です。

### `#[]` は何？

`#[]` は「この定義に追加情報を付ける」ための記法です。

JavaScriptにはほぼ直接対応する文法はありません。
デコレータに少し近いですが、Rustではもっと広く使います。

### `derive(...)`

これは、「この型に自動で便利機能を追加する」という意味です。

ここで付けているのは次の2つです。

* `Debug`
  デバッグ表示できるようにする
* `Serialize`
  JSONなどに変換できるようにする

JavaScriptでは、オブジェクトは最初から表示したりJSON化したりしやすいですが、
Rustではそうした機能を明示的に付けることがあります。

---

## 5. `pub struct BranchSales`

```rs
pub struct BranchSales {
    pub branch: String,
    pub total_sales: f64,
    pub transaction_count: usize,
}
```

これは **構造体(struct)** の定義です。

構造体は、JavaScriptでいうと「決まった形のオブジェクト」に近いです。

JavaScriptならイメージとしてはこうです。

```js
const branchSales = {
  branch: "tokyo",
  total_sales: 12345.67,
  transaction_count: 20
};
```

ただしRustでは、「どういう項目を持つか」を型として先に定義します。

---

## 6. `struct` とは何か

`struct` は、複数の値をひとまとめにした型です。

この `BranchSales` は、

* `branch`: 支店名
* `total_sales`: 売上合計
* `transaction_count`: 取引件数

を持つデータ型です。

JavaScriptはオブジェクトをその場で作れますが、Rustでは
こうして **設計図を先に書く** ことが多いです。

---

## 7. `pub` の意味

```rs
pub struct BranchSales
```

`pub` は **公開(public)** という意味です。

つまり、この `BranchSales` は他のモジュールからも使えます。

JavaScriptなら `export` に近いです。

```js
export class BranchSales {}
```

のような感覚です。

### フィールドにも `pub` がある

```rs
pub branch: String,
pub total_sales: f64,
pub transaction_count: usize,
```

これも重要です。

Rustでは、構造体自体が公開でも、**中のフィールドは別で公開指定が必要**です。

つまり、

* `pub struct` → 型そのものを公開
* `pub branch` → そのプロパティも外から見える

ということです。

JavaScriptではあまり意識しませんが、Rustでは公開範囲が細かいです。

---

## 8. フィールドの型

### `String`

```rs
pub branch: String,
```

これは所有する文字列です。

JavaScriptの `string` に近いです。

---

### `f64`

```rs
pub total_sales: f64,
```

これは 64ビット浮動小数点数です。
小数を扱う数値型です。

JavaScriptでは数値は基本全部 `number` ですが、Rustでは用途に応じて型が分かれます。

---

### `usize`

```rs
pub transaction_count: usize,
```

これは件数や添字に使う整数型です。

JavaScript初心者向けには「整数の一種」と思って大丈夫です。

---

## 9. `BranchSalesReport`

```rs
#[derive(Debug, Serialize)]
pub struct BranchSalesReport {
    pub rows: Vec<BranchSales>,
}
```

これは `BranchSales` を複数まとめた、**レポート全体**です。

JavaScriptならこんな感じです。

```js
const report = {
  rows: [
    { branch: "tokyo", total_sales: 1000, transaction_count: 3 },
    { branch: "osaka", total_sales: 800, transaction_count: 2 }
  ]
};
```

### `Vec<BranchSales>`

これは「`BranchSales` の配列」です。

前回も出てきましたが、`Vec<T>` は Rust の可変長配列です。

JavaScriptなら:

```js
Array<BranchSales>
```

に近いです。

---

# フロントエンドから呼ぶ関数

---

## 10. `#[tauri::command]`

```rs
#[tauri::command]
```

これも属性です。

これは **この関数を Tauri のフロントエンドから呼べるコマンドにする** という意味です。

つまり、この属性が付くことで、JavaScript側から `invoke` できるようになります。

JavaScript側ではだいたい次のように呼びます。

```js
import { invoke } from "@tauri-apps/api/core";

const report = await invoke("load_branch_sales");
```

つまり、この1行の属性があることで、
ただの Rust 関数が「フロントエンド公開API」になります。

---

## 11. 関数定義

```rs
fn load_branch_sales() -> Result<BranchSalesReport, String> {
```

これは通常の関数定義です。

* `fn` = 関数定義
* `load_branch_sales` = 関数名
* `()` = 引数なし
* `->` = 戻り値の型
* `Result<BranchSalesReport, String>` = 成功なら `BranchSalesReport`、失敗なら `String`

JavaScriptで感覚的に書くとこうです。

```js
function loadBranchSales() {
  // 成功なら report を返す
  // 失敗ならエラー文字列相当を返す
}
```

ただし Rust では、**失敗の型まで含めて戻り値の型に書く**のがポイントです。

---

## 12. 本体の中身

```rs
let rows = load_branch_sales_rows()?;
Ok(BranchSalesReport { rows })
```

とてもシンプルです。

やっていることは2つだけです。

1. `load_branch_sales_rows()` で配列を取る
2. それを `BranchSalesReport` に包んで返す

---

### `let rows = ...`

```rs
let rows = load_branch_sales_rows()?;
```

前回と同じく、`?` が重要です。

意味は、

* `load_branch_sales_rows()` を呼ぶ
* 成功したら中身の `rows` を取り出す
* 失敗したらこの関数も即終了して `Err(...)` を返す

JavaScript風に展開すると、だいたいこうです。

```js
const result = loadBranchSalesRows();
if (result.error) {
  return result.error;
}
const rows = result.value;
```

---

### `Ok(BranchSalesReport { rows })`

```rs
Ok(BranchSalesReport { rows })
```

これは `BranchSalesReport` 構造体を作って、それを成功値として返しています。

JavaScriptなら:

```js
return {
  rows: rows
};
```

にかなり近いです。

しかも Rust では、フィールド名と変数名が同じなら省略できるので、

```rs
BranchSalesReport { rows }
```

は省略なしで書くと、

```rs
BranchSalesReport { rows: rows }
```

です。

---

# Tauriアプリの起動部分

---

## 13. `#[cfg_attr(mobile, tauri::mobile_entry_point)]`

```rs
#[cfg_attr(mobile, tauri::mobile_entry_point)]
```

これは少し難しいですが、意味としては
**モバイル向けビルドのときだけ特別な属性を付ける**です。

### `cfg_attr`

条件付きで属性を付けるための機能です。

* `mobile` という条件のとき
* `tauri::mobile_entry_point` を付ける

JavaScriptにはあまりない考え方ですが、
「ビルド条件によって設定を変える仕組み」と思えば大丈夫です。

大事なのは、この行があっても、普通にデスクトップ向けとして読むときは
「起動設定に関するおまじない」くらいに考えて問題ありません。

---

## 14. `pub fn run()`

```rs
pub fn run() {
```

これは Tauri アプリを起動する公開関数です。

前の `load_branch_sales` は `fn` だけでしたが、こちらは `pub fn` です。
つまり外から呼べます。

JavaScriptなら:

```js
export function run() {
}
```

に近いです。

---

## 15. メソッドチェーン

```rs
tauri::Builder::default()
    .plugin(tauri_plugin_opener::init())
    .invoke_handler(tauri::generate_handler![load_branch_sales])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
```

ここは Rust というより、Tauri の設定を**つなげて書く**部分です。

JavaScriptならこんな雰囲気です。

```js
TauriBuilder.default()
  .plugin(initOpener())
  .invokeHandler([loadBranchSales])
  .run(generateContext());
```

---

## 16. `tauri::Builder::default()`

```rs
tauri::Builder::default()
```

Tauri アプリの設定を作り始めています。

### `::` は何？

Rust の `::` は、名前空間や関連関数をたどる記法です。

JavaScriptでいえば `.` に近いですが、完全には同じではありません。

* `tauri::Builder`
  `tauri` の中の `Builder`
* `Builder::default()`
  `Builder` 型にある `default` 関数を呼ぶ

`default()` は「標準設定で作る」という意味です。

---

## 17. `.plugin(...)`

```rs
.plugin(tauri_plugin_opener::init())
```

これはプラグインを追加しています。

`tauri_plugin_opener` は、ファイルやURLを開く機能に関係するプラグインです。

### `tauri_plugin_opener::init()`

これも `::` で名前をたどっています。

JavaScriptなら、

```js
plugin(opener.init())
```

っぽい感覚です。

---

## 18. `.invoke_handler(...)`

```rs
.invoke_handler(tauri::generate_handler![load_branch_sales])
```

ここがとても重要です。

これは **フロントエンドから呼べるコマンドを登録する** 部分です。

つまり、`load_branch_sales` という関数を
Tauri の `invoke` で呼べるようにしています。

JavaScript側で言うと、次のような関係です。

```js
await invoke("load_branch_sales");
```

この `"load_branch_sales"` が使えるのは、ここで登録しているからです。

---

## 19. `generate_handler![]` の `!` は何？

```rs
tauri::generate_handler![load_branch_sales]
```

Rustの `!` は **マクロ** を表します。

これは関数ではなく、コードを生成する仕組みです。

### 関数との違い

* 関数: 値を受け取って結果を返す
* マクロ: ソースコードの形を展開する

JavaScriptには直接対応するものは少ないですが、
「便利なコード生成の仕組み」と考えると分かりやすいです。

ここでは
`load_branch_sales` を Tauri のハンドラとして登録するコード
を生成しています。

---

## 20. `.run(...)`

```rs
.run(tauri::generate_context!())
```

これでアプリを実際に起動します。

`generate_context!()` もマクロです。
Tauri アプリに必要な設定情報をまとめて作って渡しています。

JavaScriptなら感覚的には、

```js
runApp(loadConfig())
```

のようなものです。

---

## 21. `.expect(...)`

```rs
.expect("error while running tauri application");
```

これは `run(...)` が失敗したときに、指定したメッセージで停止させます。

### `expect`

Rustでは `Result` や `Option` に対して使うことが多いです。

意味は、

* 成功なら中身を取り出す
* 失敗なら指定メッセージ付きで異常終了する

です。

JavaScriptならだいたい、

```js
if (result.error) {
  throw new Error("error while running tauri application");
}
```

のような感覚です。

---

# この `lib.rs` と前回の `csv_processing.rs` の関係

この2つのファイルは、役割分担がはっきりしています。

## `csv_processing.rs`

実際のCSV処理を担当

* フォルダを探す
* CSVを読む
* 金額を集計する
* 支店ごとの配列を返す

## `lib.rs`

アプリ全体との接続を担当

* データ型を定義する
* 集計関数を呼ぶ
* Tauriコマンドとして公開する
* アプリ起動時に登録する

つまり、

* `csv_processing.rs` は **中身の仕事**
* `lib.rs` は **Tauriとの窓口**

です。

---

# 処理の流れを順番に追う

ユーザーがフロントエンドで「売上一覧を読み込む」ボタンを押したとします。
すると流れはこうなります。

1. フロントエンドが `invoke("load_branch_sales")` を呼ぶ
2. Tauri が `lib.rs` の `load_branch_sales()` を実行する
3. `load_branch_sales()` が `load_branch_sales_rows()` を呼ぶ
4. `csv_processing.rs` が CSV を全部読んで集計する
5. `Vec<BranchSales>` が返る
6. `lib.rs` がそれを `BranchSalesReport { rows }` に包む
7. `Serialize` によって JSON っぽい形でフロントへ返せる
8. フロントエンドで一覧表示する

---

# JavaScript初心者向けに、特に覚えておくとよいRust文法

この `lib.rs` で大事なのは次のあたりです。

## `mod`

モジュール宣言

```rs
mod csv_processing;
```

## `use`

他の場所の名前を使いやすくする

```rs
use crate::csv_processing::load_branch_sales_rows;
```

## `struct`

オブジェクトの設計図

```rs
pub struct BranchSales { ... }
```

## `pub`

公開

```rs
pub struct ...
pub field: ...
pub fn ...
```

## `#[derive(...)]`

便利機能を自動追加

```rs
#[derive(Debug, Serialize)]
```

## `#[tauri::command]`

フロントエンドから呼べる関数にする

```rs
#[tauri::command]
fn load_branch_sales() ...
```

## `Result<T, E>`

成功か失敗かを表す

```rs
Result<BranchSalesReport, String>
```

## `?`

失敗したらそのまま返す

```rs
let rows = load_branch_sales_rows()?;
```

## マクロ `!`

コード生成の仕組み

```rs
tauri::generate_handler![load_branch_sales]
tauri::generate_context!()
```

---

# JavaScriptで書くと雰囲気はこうなる

かなり雑に、考え方だけ合わせて書くとこんな感じです。

```js
import { loadBranchSalesRows } from "./csv_processing.js";

class BranchSalesReport {
  constructor(rows) {
    this.rows = rows;
  }
}

function loadBranchSales() {
  const rows = loadBranchSalesRows();
  return new BranchSalesReport(rows);
}

function run() {
  const app = TauriBuilder.default();
  app.plugin(openerInit());
  app.invokeHandler({
    load_branch_sales: loadBranchSales
  });
  app.run(generateContext());
}
```

もちろん実際の Tauri Rust コードとは違いますが、
役割の対応を見るには分かりやすいです。

---

# このコードのよいところ

この `lib.rs` は小さいですが、かなりきれいです。

## 1. 役割が明確

* CSV処理は別ファイル
* ここでは接続だけ担当

## 2. 型がはっきりしている

* 支店1件の型
* レポート全体の型
  が分かれていて見やすいです。

## 3. Tauriとの橋渡しが簡潔

`#[tauri::command]` と `invoke_handler(...)` で、
「どの関数を公開するか」が分かりやすいです。

---

# ひとことでまとめると

この `lib.rs` は、

**CSV集計ロジックを、Tauri のフロントエンドから安全に呼べる形に整えているファイル**

です。

* `struct` で返すデータの形を決める
* `#[tauri::command]` で公開APIにする
* `run()` で Tauri に登録する

という流れになっています。





