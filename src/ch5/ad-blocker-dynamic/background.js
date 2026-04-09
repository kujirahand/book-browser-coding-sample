// PythonのAPIサーバーのエンドポイントURL --- (*1)
const API_BASE = "http://127.0.0.1:8000";
// 広告ブロックルールをAPIサーバーから取得する関数 --- (*2)
async function fetchRules(targetUrl = "") {
  const endpoint = new URL(`${API_BASE}/rules`);
  if (targetUrl) {
    endpoint.searchParams.set("url", targetUrl);
  }
  const res = await fetch(endpoint.toString());
  if (!res.ok) {
    throw new Error(`rule fetch failed: ${res.status}`);
  }
  const payload = await res.json();
  return Array.isArray(payload.rules) ? payload.rules : [];
}
// 現在アクティブなタブのURLを取得する関数 --- (*3)
async function getCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.url ?? "";
}
// APIサーバーからルールを取得してDNRの動的ルールを更新する関数 --- (*4)
async function syncDynamicRules(targetUrl = "") {
  const rules = await fetchRules(targetUrl);
  const current = await chrome.declarativeNetRequest.getDynamicRules();
  const removeRuleIds = current.map((rule) => rule.id);
  const addRules = rules;
  // DNRの動的ルールを一括更新 --- (*5)
  await chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds,
    addRules
  });
  // 最終同期日時とルール数をローカルストレージに保存 --- (*6)
  await chrome.storage.local.set({
    lastSyncAt: new Date().toISOString(),
    lastSyncCount: addRules.length
  });
  return addRules.length;
}
// 拡張機能のインストール時とブラウザ起動時にルールを同期 --- (*7)
chrome.runtime.onInstalled.addListener(() => {
  syncDynamicRules("").catch((err) => {
    console.error("sync on install failed:", err);
  });
});
// ブラウザ起動時にルールを同期 --- (*8)
chrome.runtime.onStartup.addListener(() => {
  syncDynamicRules("").catch((err) => {
    console.error("sync on startup failed:", err);
  });
});
// ポップアップからルールの同期をリクエストされたときに処理する --- (*9)
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "syncRules") {
    return false;
  }
  // ルールの同期処理を非同期で実行 --- (*10)
  (async () => {
    try {
      const targetUrl = message.withActiveTabUrl ? await getCurrentTabUrl() : "";
      const count = await syncDynamicRules(targetUrl);
      sendResponse({ ok: true, count });
    } catch (error) {
      sendResponse({
        ok: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  })();
  return true;
});
