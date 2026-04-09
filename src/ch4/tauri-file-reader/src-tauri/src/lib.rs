use tauri::Manager; // Tauriの管理マネージャーを利用

// フロントエンドで利用するRustの関数を定義 --- (※1)
#[tauri::command]
fn read_file(app: tauri::AppHandle, filename: &str) -> String {
    // デスクトップにあるファイルを読み出して返す
    let desktop_dir = app.path().desktop_dir().unwrap();
    let file_path = desktop_dir.join(filename);
    std::fs::read_to_string(file_path).unwrap_or_else(
        |err| format!(
            "ファイルが読めません。デスクトップに{filename}を配置してください: {err}"))
}
// 関数をTauriに登録してアプリを起動 --- (※2)
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            read_file // フロントエンドから呼び出せる関数を登録 --- (※3)
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
