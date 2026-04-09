const { invoke } = window.__TAURI__.core;

window.addEventListener("DOMContentLoaded", () => {
  // DOM要素を取得 --- (*1)
  const formEl = document.querySelector("#download-form");
  const urlInputEl = document.querySelector("#target-url");
  const statusMsgEl = document.querySelector("#status-msg");
  const imageUrlsEl = document.querySelector("#image-urls");
  const filesEl = document.querySelector("#downloaded-files");
  // ダウンロードボタンを押した時の処理 --- (*2)
  async function collectAndDownload() {
    // ユーザーが入力したURLを取得 --- (*3)
    const pageUrl = urlInputEl.value.trim();
    if (!pageUrl) {
      statusMsgEl.textContent = "URLを入力してください。";
      return;
    }
    statusMsgEl.textContent = "画像URLを収集中...";
    imageUrlsEl.innerHTML = "";
    filesEl.innerHTML = "";
    try {
      // Rustの関数を呼び出して画像URLを収集 --- (*4)
      const urls = await invoke("collect_images", { url: pageUrl });
      if (!Array.isArray(urls) || urls.length === 0) {
        statusMsgEl.textContent = "画像が見つかりませんでした。";
        return;
      }
      // 収集したURLをリストに描画 --- (*5)
      renderList(imageUrlsEl, urls);
      statusMsgEl.textContent = `画像をダウンロード中...`;
      // Rustの関数を実行してダウンロード開始 --- (*6)
      const downloaded = await invoke("download", {urls});
      renderList(filesEl, downloaded);
      statusMsgEl.textContent = `${downloaded.length} 件ダウンロードしました。`;
    } catch (err) {
      const message = typeof err === "string" ? err : "処理に失敗しました。";
      statusMsgEl.textContent = `エラー: ${message}`;
    }
  }
  // ダウンロードボタンを押した時のイベント ---- (*7)
  formEl.addEventListener("submit", (e) => {
    e.preventDefault();
    collectAndDownload();
  });
  // リストに値を表示するする関数
  function renderList(container, items) {
    container.innerHTML = ""; // 既存の内容をクリア
    for (const item of items) {
      const li = document.createElement("li");
      li.textContent = item;
      container.appendChild(li);
    }
  }
});
