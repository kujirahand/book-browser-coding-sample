// API呼び出しを行う関数群

// APIからのレスポンスをJSONとして安全に解析する関数
async function parseJson(response) {
  try {
    return await response.json();
  } catch (_err) {
    return {};
  }
}

// ファイルリストを取得する関数
export async function apiGetFiles() {
  const response = await fetch("/api/files");
  return { ok: response.ok, status: response.status, data: await parseJson(response) };
}

// ファイルの内容を取得する関数
export async function apiGetFile(fileName) {
  const response = await fetch(`/api/file/${encodeURIComponent(fileName)}`);
  return { ok: response.ok, status: response.status, data: await parseJson(response) };
}

// ファイルを保存する関数
export async function apiSave(payload) {
  const response = await fetch("/api/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return { ok: response.ok, status: response.status, data: await parseJson(response) };
}

// 質問を送信して回答を取得する関数
export async function apiAsk(question) {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return { ok: response.ok, status: response.status, data: await parseJson(response) };
}

// テキストを要約する関数
export async function apiSummarize(focus) {
  const response = await fetch("/api/summarize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ focus }),
  });
  return { ok: response.ok, status: response.status, data: await parseJson(response) };
}

// 作図を生成する関数
export async function apiDiagram(payload) {
  const response = await fetch("/api/diagram", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return { ok: response.ok, status: response.status, data: await parseJson(response) };
}
