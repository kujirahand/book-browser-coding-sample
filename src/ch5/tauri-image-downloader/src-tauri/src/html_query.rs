use std::collections::HashSet;
use scraper::{Html, Selector};

// URLを指定するとそのURLから画像を収集する関数 --- (*1)
#[tauri::command]
pub async fn collect_images(url: String) -> Result<Vec<String>, String> {
    // URLからHTMLを取得 --- (*2)
    let response = match reqwest::get(&url).await {
        Ok(response) => response,
        Err(_) => return Err("URLが開けません".to_string()),
    };
    let body = match response.text().await {
        Ok(body) => body,
        Err(_) => return Err("URLから取得したデータが不正".to_string()),
    };
    // img要素の一覧を取得するセレクタを準備 --- (*3)
    let selector = match Selector::parse("img") {
        Ok(selector) => selector,
        Err(_) => return Err("セレクタ指定の間違い".to_string()),
    };
    // 基準となるURLを得るための解析 --- (*4)
    let base_url = reqwest::Url::parse(&url).ok();
    // HTMLを解析 --- (*5)
    let document = Html::parse_document(&body);
    let mut seen = HashSet::new(); // 重複チェック用のセット
    let mut images = Vec::new(); // 画像URLのリスト
    // img要素の一覧を取得して、src属性からURLを抜き取る --- (*6)
    for element in document.select(&selector) {
        // src属性を取り出す
        let Some(src) = element.value().attr("src") else {
            continue;
        };
        let src = src.trim();
        if src.is_empty() {
            continue;
        }
        // URLを絶対URLに変換 --- (*7)
        let resolved = match &base_url {
            Some(base) => base
                .join(src).map(|u| u.to_string())
                .unwrap_or_else(|_| src.to_string()),
            None => src.to_string(),
        };
        // 重複でなければ画像URLのリストに追加
        if seen.insert(resolved.clone()) {
            images.push(resolved);
        }
    }
    Ok(images) // 画像URLのリストを返す --- (*8)
}
