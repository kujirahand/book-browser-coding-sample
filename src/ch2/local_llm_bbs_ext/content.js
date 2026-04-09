// Webページに注入されるコンテンツスクリプト

// ページにボタンを追加してLLM応答を挿入 --- (*1)
function addLLMButton() {
  // すでにボタンがある場合は追加しない
  if (document.getElementById('llm-insert-button')) {
    return;
  }
  // フローティングボタンを作成
  const button = document.createElement('button');
  button.id = 'llm-insert-button';
  button.textContent = 'LLMの応答を挿入';
  button.style.position = 'fixed';
  button.style.bottom = '20px';
  button.style.right = '20px';
  button.style.zIndex = '10000';
  button.style.padding = '8px 16px';
  button.style.background = '#993030';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '6px';
  button.style.cursor = 'pointer';
  button.style.fontSize = '15px';  
  button.addEventListener('click', insertLLMResponse);
  document.body.appendChild(button);
}

// LLM応答をテキストボックスに挿入 --- (*2)
async function insertLLMResponse() {
  const button = document.getElementById('llm-insert-button');
  button.textContent = '⏳ 処理中...';
  button.disabled = true;
  try {
    // manatu掲示板にある.itemの要素を検索 --- (*3)
    const items = document.querySelectorAll('.item');
    let prompt;
    if (items.length > 0) {
      // div.itemが見つかった場合、全てのテキストを収集
      const itemTexts = Array.from(items)
        .map(item => item.textContent.trim())
        .filter(text => text.length > 0)
        .join('\n\n');
      // プロンプトを組み立てる --- (*4)
      prompt = `あなたは掲示板の管理者です。
        以下は掲示板に書き込まれた内容です。
        適切な応答を生成してください：\n\n${itemTexts}`;
      console.log(`${items.length}個のdiv.itemを見つけました`);
    } else {
      // div.itemが見つからない場合、適当なテキストを生成
      prompt = '便利な掲示板を利用して欲しい旨の案内を丁寧に書いてください。';
      console.log('div.itemが見つかりませんでした。適当な案内を生成します。');
    }
    // LM Studioと通信 --- (*5)
    const response = await chrome.runtime.sendMessage({
      action: 'queryLLM',
      prompt: prompt
    });
    if (response.success) {
      // テキストボックスを探して挿入
      insertIntoTextbox(response.text);
    } else {
      alert(`エラー: ${response.error}\n\nLM Studioが起動しているか確認してください。`);
    }
  } catch (error) {
    console.error('エラー:', error);
    alert(`エラーが発生しました: ${error.message}`);
  } finally {
    button.textContent = 'LLMの応答を挿入';
    button.disabled = false;
  }
}

// テキストボックスにテキストを挿入 --- (*6)
function insertIntoTextbox(text) {
  // テキストボックスな要素を探す --- (*7)
  const textInputs = [
    ...document.querySelectorAll('textarea'),
    ...document.querySelectorAll('input[type="text"]'),
  ];
  // 選択されているテキスト入力要素を優先
  let targetElement = document.activeElement;
  if (!textInputs.includes(targetElement)) {
    // フォーカスされていない場合は、最初のテキスト入力要素を使用
    targetElement = textInputs[0];
  }
  if (!targetElement) {
    alert('テキストボックスが見つかりませんでした。');
    return;
  }
  // テキストボックスにテキストを設定 --- (*8)
  targetElement.value = text;
  targetElement.dispatchEvent(new Event('input', { bubbles: true }));
  targetElement.dispatchEvent(new Event('change', { bubbles: true }));
  targetElement.focus(); // フォーカスを当てる
  console.log('LLMの応答を挿入しました', text);
}
// ページ読み込み時にボタンを追加 --- (*9)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addLLMButton);
} else {
  addLLMButton();
}
