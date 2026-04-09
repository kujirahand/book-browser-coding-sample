// ブラウザ拡張 - バックグラウンドのスクリプト
// 管理サーバーのAPIエンドポイント
const API_BASE = "http://127.0.0.1:8000";
// コンテキストメニューIDを定義
const MENU_ID = "idea-bank-save-selection";

// 拡張機能がインストールされたときのイベント --- (*1)
chrome.runtime.onInstalled.addListener(() => {
  // コンテキストメニューを作成 --- (*2)
  chrome.contextMenus.create({
    id: MENU_ID, // メニューID
    title: "アイデアバンクに保存", // メニューのタイトル
    contexts: ["selection"] // テキスト選択時にメニューを表示
  });
});
// 通知を表示する関数 --- (*3)
function notify(title, message) {
  chrome.notifications.create({ // 通知を作成
    type: "basic",
    iconUrl: chrome.runtime.getURL("icon128.png"),
    title,
    message
  });
}
// タブから選択テキストを取得する関数 --- (*4)
async function getSelectionFromTab(tabId) {
  try {
    // タブにメッセージを送信して選択テキストを取得
    const res = await chrome.tabs.sendMessage(tabId, {
      action: "idea-bank:get-selection" });
    if (!res || !res.text) { return null; }
    return res;
  } catch (error) {
    return null;
  }
}
// アイデアを保存する関数 --- (*5)
async function saveIdea(payload) {
  // APIエンドポイントにPOSTリクエストを送信してアイデアを保存
  const response = await fetch(`${API_BASE}/api/ideas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) { // エラーレスポンスの場合はエラーを投げる
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return await response.json();
}
// コンテキストメニューがクリックされたときのイベントリスナー --- (*6)
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  // 指定メニュー以外やタブ情報がない場合は処理しない
  if (info.menuItemId !== MENU_ID || !tab || !tab.id) {
    return;
  }
  // タブから選択テキストを取得 --- (*7)
  const selected = await getSelectionFromTab(tab.id);
  const text = selected?.text || info.selectionText || "";
  if (!text.trim()) {
    notify("アイデアバンク", "テキスト選択が見つかりませんでした。");
    return;
  }
  try {
    // サーバーにアイデアを保存 --- (*8)
    const saved = await saveIdea({
      text,
      url: selected?.url || tab.url || "",
      page_title: selected?.title || tab.title || ""
    });
    notify("保存しました", saved.title || "アイデアを保存しました");
  } catch (error) {
    notify("保存に失敗しました", "サーバーが起動しているか確認してください。");
  }
});
