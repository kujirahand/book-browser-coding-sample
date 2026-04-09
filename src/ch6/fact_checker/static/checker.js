// checker.js - フロントエンドのロジック
// APIエンドポイント --- (*1)
const API_URL = "/api/fact-check";
// DOM要素の取得
const claimEl = document.getElementById("claim");
const checkBtn = document.getElementById("checkBtn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
// ファクトチェックの実行 --- (*2)
async function runCheck() {
    // テキストエリアから主張を取得 --- (*3)
    const claim = claimEl.value.trim();
    if (!claim) {
        statusEl.textContent = "主張を入力してください。";
        return;
    }
    // UIの更新
    checkBtn.disabled = true;
    statusEl.textContent = "判定中...";
    statusEl.classList.add("loading");
    resultEl.innerHTML = "";
    try {
        // APIにPOSTリクエストを送信 --- (*4)
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ claim })
        });
        if (!res.ok) {
            const text = await res.text();
            throw new Error(text || "APIエラー");
        }
        // 結果の取得としてHTMLをレンダリング --- (*5)
        const data = await res.json();
        statusEl.textContent = "完了";
        renderResult(data);
    } catch (err) {
        statusEl.textContent = "エラー: " + err.message;
    } finally {
        checkBtn.disabled = false; // UIを元に戻す
        statusEl.classList.remove("loading");
    }
}
// ボタンにイベントリスナーを追加 --- (*6)
checkBtn.addEventListener("click", runCheck);
// HTMLエスケープ関数 --- (*7)
function esc(s) {
    return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
// 結果のレンダリング --- (*8)
function renderResult(data) {
    // 各モデルの結果をHTMLに変換 --- (*9)
    const resultsHtml = data.results.map(r => {
        const val = Number(r.confidence).toFixed(2)
        return `
        <div class="box">
            <div class="model">${esc(r.model)}</div>
            <h3>${esc(r.verdict)} (確信度: ${val})</h3>
            <p class="summary">${esc(r.summary)}</p>
            <p>${esc(r.content)}</p>
        </div>
        `;
    }).join("");
    // 最終判定と全体の要約を表示 --- (*10)
    const score = Number(data.agreement_score).toFixed(2);
    resultEl.innerHTML = `
    <div class="box">
        <h2>最終判定: ${esc(data.final_verdict)}</h2>
        <p>${esc(data.summary)}</p>
        <div class="muted">スコア: ${score}</div>
    </div>
    ${resultsHtml}
    `;
}
