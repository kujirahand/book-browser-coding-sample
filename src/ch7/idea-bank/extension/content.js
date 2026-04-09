// content.js - タブ内で選択されたテキストを取得するためのスクリプト
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  // background.jsからの特定のメッセージにのみ反応する
  if (!message || message.action !== "idea-bank:get-selection") {
    return;
  }
  // タブ内で選択されたテキストを取得し、URLとタイトルも含めてレスポンスとして返す
  const text = window.getSelection ? window.getSelection().toString().trim() : "";
  sendResponse({
    text,
    url: location.href,
    title: document.title
  });
  return true;
});
