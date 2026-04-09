// コンテンツスクリプト
const currentUrl = window.location.href; // 読み込まれたURL
console.log('[Content Script] URL=' + currentUrl);

// ページ内の全img要素からURLを抽出する関数 --- (*1)
function getAllImageUrls() {
  const images = document.querySelectorAll('img');
  const urls = Array.from(images)
    .map(img => img.src || img.dataset.src)
    .filter(url => url && url.trim() !== '');
  console.log(`[Content Script] 見つかった画像数: ${urls.length}`);
  console.log(`[Content Script] 画像URL: `, urls);
  return urls;
}

// メッセージリスナーを登録する --- (*2)
chrome.runtime.onMessage.addListener((req, sender, callback) => {
  console.log('[Content Script] メッセージ受信:', req);
  // 'getImages' アクションの場合、画像URLを取得してレスポンスを返す --- (*3)
  if (req.action === 'getImages') {
    const urls = getAllImageUrls();
    console.log('[Content Script] レスポンス送信:', urls);
    callback({images: urls}); // コールバックでレスポンスを返す
  }
});
