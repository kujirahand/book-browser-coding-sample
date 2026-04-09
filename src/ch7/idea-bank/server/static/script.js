// フロントエンド側のJavaScript
// DOM要素の取得
const listElem = document.getElementById("list");
const titleElem = document.getElementById("title");
const summaryElem = document.getElementById("summary");
const tagsElem = document.getElementById("tags");
const ideasElem = document.getElementById("ideas");
const textElem = document.getElementById("text");
const sourceElem = document.getElementById("source");
// アイデアの一覧を読み込む関数 --- (*1)
async function loadList() {
  // サーバーからアイデアの一覧を取得 --- (*2)
  const items = await fetch("/api/ideas").then((r) => r.json());
  // 取得したアイデアをリストに表示 --- (*3)
  listElem.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.dataset.id = item.id;
    li.innerHTML = `<div>${item.title}</div>` +
      `<div class="meta">${item.created_at}</div>`;
    // アイデアをクリックしたときの処理 --- (*4)
    li.addEventListener("click", async () => {
      [...listElem.children].forEach((x) => x.classList.remove("active"));
      li.classList.add("active");
      await loadIdea(item.id);
    });
    listElem.appendChild(li);
  }
  if (items.length > 0) {
    listElem.children[0].click();
  }
}
// アイデアを読み込む関数 --- (*5)
async function loadIdea(id) {
  // サーバーからアイデアの詳細を取得 --- (*6)
  const endpoint = `/api/ideas/${encodeURIComponent(id)}`;
  const idea = await fetch(endpoint).then((r) => r.json());
  // 取得したアイデアの内容を表示 --- (*7)
  titleElem.textContent = idea.title; // タイトルを表示
  summaryElem.textContent = idea.summary; // 要約を表示
  textElem.textContent = idea.text; // 本文を表示
  const titleStr = toHtml(idea.source_title || idea.source_url);
  const urlStr = toHtml(idea.source_url);
  sourceElem.innerHTML = idea.source_url
    ? `<a href="${urlStr}" target="_blank">${titleStr}</a>`
    : ""; // URLがあればリンクを表示、なければ空にする
  // タグを表示
  tagsElem.innerHTML = "";
  for (const tag of idea.tags) {
    const s = document.createElement("span");
    s.className = "tag";
    s.textContent = tag;
    tagsElem.appendChild(s);
  }
  // 発展アイデアを表示
  ideasElem.innerHTML = "";
  for (const text of idea.ideas || []) {
    const card = document.createElement("article");
    card.className = "idea-card";
    card.textContent = '📍 ' + text;
    ideasElem.appendChild(card);
  }
}
// HTMLエスケープ --- (*8)
function toHtml(text) {
  return text.replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
}
loadList();
