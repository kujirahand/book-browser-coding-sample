// 画像URLを指定してダウンロードする関数 --- (*1)
#[tauri::command]
pub async fn download(urls: Vec<String>) -> Result<Vec<String>, String> {
    let mut downloaded = Vec::new();
    // ダウンロード先のフォルダを決定 --- (*2)
    let download_root = dirs::download_dir().ok_or("フォルダ取得失敗")?;
    // 画像URLを順番にダウンロード --- (*3)
    for url in urls {
        // URLから親URLを得て、保存フォルダ名を決定 --- (*4)
        let parent = parent_url_string(&url);
        let base_dir_name = sanitize_url_for_dir(&parent);
        let save_dir = download_root.join(base_dir_name);
        // フォルダがなければ作成
        std::fs::create_dir_all(&save_dir).map_err(|_| "フォルダ作成失敗")?;
        // ファイル名を決定 --- (*5)
        let filename = url
            .split('/').last().unwrap_or("image.jpg")
            .split('?').next().unwrap_or("image.jpg");
        let path = save_dir.join(filename);
        // ダウンロード --- (*6)
        let response = match reqwest::get(&url).await {
            Ok(response) => response,
            Err(_) => continue,
        };
        let bytes = match response.bytes().await {
            Ok(bytes) => bytes,
            Err(_) => continue,
        };
        // ファイルに保存 --- (*7)
        if std::fs::write(&path, &bytes).is_ok() {
            downloaded.push(path.to_string_lossy().to_string());
        }
    }
    if downloaded.is_empty() { // 画像が空ならエラー
        Err("画像のダウンロードに失敗しました".to_string())
    } else {
        Ok(downloaded)
    }
}
// URLをファイル名に使えるように変換する関数 --- (*8)
fn sanitize_url_for_dir(url: &str) -> String {
    let url = strip_http_scheme(url);
    let mut sanitized: String = url.chars().map(|c| {
            if c.is_ascii_alphanumeric() { c } else { '_' }
        }).collect();
    if sanitized.is_empty() {
        sanitized = "unknown".to_string();
    }
    sanitized
}
// URLからクエリやフラグメントを取り除いて親URLを得る関数 --- (*9)
fn parent_url_string(url: &str) -> String {
    let Ok(mut parsed) = reqwest::Url::parse(url) else {
        return url.to_string();
    };
    parsed.set_query(None);
    parsed.set_fragment(None);
    if let Ok(mut segments) = parsed.path_segments_mut() {
        segments.pop_if_empty();
        segments.pop();
    }
    parsed.to_string()
}
// URLからhttp://やhttps://を取り除く関数 --- (*10)
fn strip_http_scheme(url: &str) -> &str {
    url.strip_prefix("https://")
        .or_else(|| url.strip_prefix("http://"))
        .unwrap_or(url)
}
