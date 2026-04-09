// ページを読み込んだ時のイベント--- (*1)
document.addEventListener('DOMContentLoaded', async () => {
  try {
    // アクティブなタブの情報を取得 --- (*2)
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const title = tab.title;
    const url = tab.url;
    const title_url = `${title}\n[URL] ${url}`;
    
    // タイトルを表示 --- (*3)
    document.getElementById('title').textContent = title_url
    
    // コピーボタンのクリックイベント --- (*4)
    const btn = document.getElementById('copyButton')
    btn.addEventListener('click', async () => {
        // クリップボードに書き込み --- (*5)
        await navigator.clipboard.writeText(title_url);
        const msgEl = document.getElementById('message');
        msgEl.textContent = 'コピーしました！';
        // 2秒後にメッセージを消す
        setTimeout(() => { msgEl.textContent = ''; }, 2000);
    });
  } catch (error) {
    document.getElementById('title').textContent = 'エラーが発生しました';
    console.error('Error:', error);
  }
});
