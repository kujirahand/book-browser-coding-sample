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
