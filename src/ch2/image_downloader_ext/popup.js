// ----------------------------------------------------------
// ブラウザ拡張を起動した時に実行するプログラム
// ----------------------------------------------------------
// 「popup.html」の要素を取得 --- (*1)
const statusEl = document.getElementById('status');
const downloadListEl = document.getElementById('downloadList');
const downloadBtn = document.getElementById('downloadBtn');
// ダウンロードボタンを押した時の処理 --- (*2)
const flagInejcted = {};
downloadBtn.addEventListener('click', async () => {  
  // ダウンロードした画像のリストをクリア
  downloadListEl.innerHTML = ''; 
  // 開いている全てのタブを取得
  const tabs = await chrome.tabs.query({currentWindow: true});
  console.log('[Popup] 取得したタブ数:', tabs.length);
  console.log('[Popup] タブ一覧:', tabs.map(t => ({id: t.id, url: t.url})));
  // コンテンツスクリプトにメッセージを送信して画像URLを取得 --- (*3)
  try {
    const allImages = []; // すべての画像URLを格納する配列
    for (const tab of tabs) { // 各タブに対して処理を実行
      console.log(`[Popup] タブ ${tab.id} (${tab.url}) へメッセージ送信`);
      try {
        // まずコンテンツスクリプトを注入 --- (*4)
        if (!flagInejcted[tab.id]) {
            console.log(`[Popup] タブ ${tab.id} へスクリプト注入`);
            await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            files: ['content.js']
            });
            flagInejcted[tab.id] = true;
        }
        // 画像URLを取得するようメッセージを送信 --- (*5)
        const response = await chrome.tabs.sendMessage(
            tab.id,
            {action: 'getImages'});
        const images = response.images || [];
        console.log(`[Popup] タブ ${tab.id} から ${images.length} 個の画像を取得`);
        allImages.push(...images);
      } catch (error) {
        console.log(`[Popup] タブ ${tab.id}: 注入失敗 (${error.message})`, tab);
      }
    }    
    // 重複を排除 --- (*6)
    const uniqueImages = [...new Set(allImages)];
    console.log('[Popup] 重複排除後の画像数:', uniqueImages.length);
    // 画像の個数を確認
    if (uniqueImages.length === 0) {
      statusEl.textContent = '画像が見つかりません';
      statusEl.className = 'info';
      return;
    }
    // ステータス表示を更新
    statusEl.textContent = `${uniqueImages.length}個の画像を処理中...`;
    statusEl.className = 'info';    
    // 画像をダウンロード --- (*7)
    uniqueImages.forEach((url, index) => {
      const filename = generateFilename(url, index);
      chrome.downloads.download({
        url: url,
        filename: filename
      });
      // ポップアップにメッセージを追加 --- (*8)
      addDownloadItem(filename, url);
    });
  } catch (error) {
    statusEl.textContent = 'エラーが発生しました: ' + error.message;
    statusEl.className = 'error';
    console.error('Error:', error);
  }
});

// ----------------------------------------------------------
// ユーティリティ関数群
// ----------------------------------------------------------
// URLを元にしてダウンロード用のファイル名を生成 --- (*9)
function generateFilename(url, index) {
    const ext = getFileExtension(url);
    const original = getCleanBasename(url);
    const now = Date.now();
    return `download${now}-${index}-${original}.${ext}`;
}
// URLから拡張子を取得
function getFileExtension(url) {
    const match = url.match(/\.([a-z0-9]+)(?:\?|$)/i);
    return match ? match[1].toLowerCase() : 'jpg';
}
// URLから拡張子なし、アルファベットと数字のみを含むベース名を取得
function getCleanBasename(url) {
    try {
        const urlObj = new URL(url);
        const pathname = urlObj.pathname;
        const basename = pathname.substring(pathname.lastIndexOf('/') + 1);
        // 拡張子を除去
        const nameWithoutExt = basename.replace(/\.[^.]+$/, '');
        // アルファベットと数字のみを残す
        const cleanName = nameWithoutExt.replace(/[^a-zA-Z0-9]/g, '');
        return cleanName || 'image';
    } catch (e) {
        return 'image';
    }
}
// ダウンロードリストに項目を追加 --- (*10)
function addDownloadItem(filename, url) {
    downloadListEl.insertAdjacentHTML('beforeend', `
        <div class="download-item">
            <div class="download-filename">${filename}</div>
            <div class="download-url">${url}</div>
        </div>
    `);
}
