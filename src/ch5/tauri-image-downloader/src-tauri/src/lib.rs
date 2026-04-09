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
