// DOM要素を取得 --- (*1)
const promptEl = document.getElementById("prompt");
const codeEl = document.getElementById("code");
const previewEl = document.getElementById("preview");
const errorEl = document.getElementById("error");
const generateBtn = document.getElementById("generate");
const fixBtn = document.getElementById("fix");

// Mermaidを初期化 --- (*2)
mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });

// API呼び出し関数 --- (*3)
async function api(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

// Mermaidコードをプレビューにレンダリング --- (*4)
async function render() {
  errorEl.textContent = "";
  previewEl.removeAttribute("data-processed");
  previewEl.textContent = codeEl.value.trim();
  try {
    await mermaid.run({ nodes: [previewEl] });
  } catch (e) {
    errorEl.textContent = e.message || String(e);
  }
}

// 生成ボタンのクリックイベント --- (*5)
generateBtn.onclick = async () => {
  generateBtn.disabled = true;
  try {
    const data = await api("/api/generate", { prompt: promptEl.value });
    codeEl.value = data.code || "";
    await render();
  } finally {
    generateBtn.disabled = false;
  }
};

// 修正ボタンのクリックイベント --- (*6)
fixBtn.onclick = async () => {
  const data = await api("/api/fix", {
    code: codeEl.value,
    error: errorEl.textContent || "parse error",
  });
  codeEl.value = data.code || codeEl.value;
  await render();
};

// コードを修正したときもプレビューを更新 --- (*7)
codeEl.addEventListener("input", () => {
  render();
});

// 初期表示用のコード --- (*8)
codeEl.value = `flowchart TD\n  A[Start] --> B[Draw Diagram] --> C[Done]`;
render();
