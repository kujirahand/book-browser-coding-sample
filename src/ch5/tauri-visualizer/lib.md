# src-tauri/src/lib.rs についての解説

この `lib.rs` は、**Tauri アプリのバックエンド側の入口**です。`csv_processing.rs` が「CSVを集計する実務処理」だったのに対して、こちらの `lib.rs` は、

* モジュールを読み込む
* 集計結果を入れるデータ型を定義する
* フロントエンドから呼べるコマンドを定義する
* Tauri アプリを起動する

という、**全体の配線役**を担当しています。

JavaScript初心者向けに、まず全体像を説明してから、**Rustの文法中心**に細かく見ていきます。

---


# `tauri-src/lib.rs`このファイルの役目

続けて、もう一つのファイルのRustのプログラムの説明を行います。
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

つまり、 `csv_processing.rs` がこの `lib.rs` から見えるようになります。

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

# この `lib.rs` と `csv_processing.rs` の関係

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
