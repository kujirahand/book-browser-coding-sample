// LM Studioとの通信を行うバックグラウンドスクリプト

// LM Studio APIと通信する関数 --- (*1)
async function queryLMStudio(prompt) {
  // LM StudioのエンドポイントURL --- (*2)
  const LM_STUDIO_URL = 'http://localhost:1234/v1/chat/completions';
  try {
    // LM Studioのチャット補完エンドポイントにPOSTリクエストを送信 --- (*3)
    const response = await fetch(LM_STUDIO_URL, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        model: 'local-model', // 使用するモデル名を指定 --- (*4)
        messages: [ // チャットメッセージの配列 --- (*5)
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 500 // 応答の最大トークン数
      })
    });
    if (!response.ok) {
      throw new Error(`LM Studio API error: ${response.status}`);
    }
    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('LM Studio通信エラー:', error);
    throw error;
  }
}

// content scriptからのメッセージを受信 --- (*6)
chrome.runtime.onMessage.addListener((req, sender, sendRes) => {
  if (req.action === 'queryLLM') { // アクションを確認 --- (*7)
    // LM Studioと通信して返信 --- (*8)
    queryLMStudio(req.prompt)
      .then(response => {
        sendRes({ success: true, text: response });
      })
      .catch(error => {
        sendRes({ success: false, error: error.message });
      });
    return true; // 非同期レスポンスを示す
  }
});
