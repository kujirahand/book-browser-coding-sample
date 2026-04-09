// APIサーバーのベースURL
const API_BASE = "http://127.0.0.1:8000";
// ポップアップ画面のUI要素を取得 --- (*1)
const statusEl = document.getElementById("status");
const domainsEl = document.getElementById("domains");
const syncBtn = document.getElementById("syncBtn");
// ステータスメッセージを表示する関数 --- (*2)
function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}
// ボタンの有効/無効を切り替える関数 --- (*3)
function setButtonsDisabled(disabled) {
  syncBtn.disabled = disabled;
}
// 広告ブロックルールをAPIサーバーから取得する関数 --- (*4)
async function loadDomains() {
  const res = await fetch(`${API_BASE}/domains`);
  if (!res.ok) {
    throw new Error(`ドメイン一覧の取得に失敗: ${res.status}`);
  }
  const payload = await res.json();
  const domains = Array.isArray(payload.domains) ? payload.domains : [];
  domainsEl.value = domains.join("\n");
}
// ドメイン一覧をAPIサーバーに保存する関数 --- (*5)
async function saveDomains() {
  const body = new URLSearchParams({ domains: domainsEl.value });
  const res = await fetch(`${API_BASE}/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString()
  });
  if (!res.ok) {
    throw new Error(`保存に失敗: ${res.status}`);
  }
  const payload = await res.json();
  return payload.count ?? 0;
}
// DNRのルールをAPIサーバーから取得して更新する関数 --- (*6)
async function syncRules() {
  // ポップアップからbackground.jsにルールの同期をリクエスト --- (*7)
  const result = await chrome.runtime.sendMessage({
    type: "syncRules",
    withActiveTabUrl: true
  });
  if (!result?.ok) {
    throw new Error(result?.error ?? "同期に失敗しました");
  }
  return result.count ?? 0;
}
// 「保存して同期」のボタンがクリックされたときの処理 --- (*8)
syncBtn.addEventListener("click", async () => {
  setButtonsDisabled(true);
  setStatus("保存して同期中...");
  try {
    await saveDomains(); // ドメイン一覧をAPIサーバーに保存
    const count = await syncRules(); // DNRのルールを更新
    setStatus(`${count}件のルールを適用しました`);
  } catch (error) {
    setStatus(
      error instanceof Error ? error.message : "保存または同期に失敗しました",
      true
    );
  } finally {
    setButtonsDisabled(false);
  }
});
// ページが読み込まれたときにドメイン一覧をAPIサーバーから取得して表示 --- (*9)
loadDomains()
  .then(() => {
    setStatus("ドメイン一覧を読み込みました");
  })
  .catch((err) => {
    setStatus(String(err), true);
  });
