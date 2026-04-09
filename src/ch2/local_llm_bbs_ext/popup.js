// ポップアップのスクリプト
// ボタンをクリックした時の処理 --- (*1)
document.getElementById('testButton')
        .addEventListener('click', async () => {
  const button = document.getElementById('testButton');
  button.textContent = '接続中...';
  button.disabled = true;

  try {
    // LM StudioにGETリクエストを送信 --- (*2)
    const response = await fetch(
        'http://localhost:1234/v1/models', {
      method: 'GET',
      headers: {'Content-Type': 'application/json'}
    });
    if (response.ok) {
      button.textContent = '✓ 接続成功！';
      button.style.background = '#10b981';
      button.style.color = 'white';
      // モデル一覧をコンソールに表示 --- (*3)
      const data = await response.json();
      console.log('LM Studioモデル一覧:', data);
    } else {
      throw new Error('接続失敗');
    }
    button.disabled = false;
  } catch (error) {
    // LM Studioに接続できなかった場合の処理 --- (*4)
    button.textContent = '✗ 接続失敗';
    button.style.background = '#ef4444';
    button.style.color = 'white';
    alert('LM Studioに接続できませんでした。\n' +
        'http://localhost:1234 でLM Studioが起動しているか確認してください。');
  }
});
