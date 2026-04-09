use std::fs;
use std::path::{Path, PathBuf};

use crate::BranchSales;

const ERR_IO: &str = "CSVの読み込みに失敗しました。";
const ERR_CSV_FORMAT: &str = "CSVの形式が不正です。";

// 支店CSVを走査して売上集計結果の一覧を返す --- (*1)
pub fn load_branch_sales_rows() -> Result<Vec<BranchSales>, String> {
    // CSVフォルダのパスを取得
    let data_dir = get_csv_dir()?;
    // CSVファイルを走査して集計 --- (*2)
    let mut rows = vec![];
    for entry in fs::read_dir(&data_dir).map_err(|_| ERR_IO.to_string())? {
        let path = entry
            .map_err(|_| ERR_IO.to_string())?
            .path();
        if !is_branch_csv(&path) { // 集計対象外のファイルはスキップ
            continue;
        }
        // ファイル名から支店IDを取り出す --- (*3)
        let branch = branch_id_from_path(&path);
        // 集計して売上合計と取引件数を取得 --- (*4)
        let (total_sales, transaction_count) = summarize_csv_file(&path)?;
        rows.push(BranchSales {
            branch,
            total_sales,
            transaction_count,
        });
    }
    // 売上合計でソート --- (*5)
    rows.sort_by(|a, b| {
        b.total_sales
            .partial_cmp(&a.total_sales)
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    // 集計結果が空ならエラーにする
    if rows.is_empty() {
        return Err("支店CSVが見つかりませんでした。".to_string());
    }
    Ok(rows)
}

// Documents/demo_keiri の実パスを取得する --- (*6)
fn get_csv_dir() -> Result<PathBuf, String> {
    let documents_dir = dirs::document_dir()
        .ok_or_else(|| "ドキュメントフォルダが見つかりません。".to_string())?;

    let dir = documents_dir.join("demo_keiri");
    if dir.is_dir() {
        Ok(dir)
    } else {
        Err("CSVフォルダが見つかりません。".to_string())
    }
}

// 集計対象の支店CSVかどうかを判定する --- (*7)
fn is_branch_csv(path: &Path) -> bool {
    let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
        return false;
    };
    let lower = name.to_ascii_lowercase();
    if !lower.starts_with("branch_") || !lower.ends_with(".csv") {
        return false;
    }
    true
}

// ファイル名 branch_xxx.csv から支店ID(xxx)を取り出す --- (*8)
fn branch_id_from_path(path: &Path) -> String {
    let file_stem = path
        .file_stem()
        .and_then(|name| name.to_str())
        .unwrap_or("branch_unknown");

    if let Some((_, suffix)) = file_stem.split_once('_') {
        suffix.to_string()
    } else {
        file_stem.to_string()
    }
}

// 1つのCSVを読み、売上合計と取引件数を計算する --- (*9)
fn summarize_csv_file(path: &Path) -> Result<(f64, usize), String> {
    // CSVリーダーを生成 --- (*10)
    let mut reader = csv::ReaderBuilder::new()
        .has_headers(true)
        .from_path(path)
        .map_err(|_| ERR_IO.to_string())?;
    // 7列目(0から数えて6番目)の金額を走査して集計 --- (*11)
    let mut total_sales = 0.0;
    let mut transaction_count = 0;
    for row in reader.records() {
        let row = row.map_err(|_| ERR_CSV_FORMAT.to_string())?;
        if let Some(value) = row.get(6) {
            total_sales += parse_number(value);
            transaction_count += 1;
        }
    }
    Ok((total_sales, transaction_count))
}

// 金額文字列から数値変換に不要な文字を除去して数値化　--- (*12)
fn parse_number(input: &str) -> f64 {
    let normalized: String = input
        .chars()
        .filter(|ch| ch.is_ascii_digit() || *ch == '.' || *ch == '-')
        .collect();

    normalized.parse::<f64>().unwrap_or(0.0)
}
