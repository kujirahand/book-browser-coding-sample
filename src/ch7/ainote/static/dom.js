// DOM要素の取得と操作を行う関数群
export const domElements = {
  editModeBtn: document.getElementById("editModeBtn"),
  qaModeBtn: document.getElementById("questionModeBtn"),
  newFileBtn: document.getElementById("newFileBtn"),
  fileListEl: document.getElementById("fileList"),
  editPanel: document.getElementById("editPanel"),
  questionPanel: document.getElementById("questionPanel"),
  fileNameInput: document.getElementById("fileNameInput"),
  editor: document.getElementById("editor"),
  saveBtn: document.getElementById("saveBtn"),
  questionInput: document.getElementById("questionInput"),
  askBtn: document.getElementById("askBtn"),
  summarizeBtn: document.getElementById("summarizeBtn"),
  drawBtn: document.getElementById("drawBtn"),
  answerOutput: document.getElementById("answerOutput"),
  diagramOutput: document.getElementById("diagramOutput"),
};

// Mermaidとmarkedの初期化を行う関数
export function domInitRenderers() {
  mermaid.initialize({ startOnLoad: false });
  if (!window.marked) return;
  const renderer = new marked.Renderer();
  renderer.html = () => "";
  marked.setOptions({ gfm: true, breaks: true, renderer });
}

// 編集モードと質問モードを切り替える関数
export function domSetMode(mode) {
  const isEdit = mode === "edit";
  domElements.editPanel.classList.toggle("hidden", !isEdit);
  domElements.questionPanel.classList.toggle("hidden", isEdit);
  domElements.editModeBtn.classList.toggle("active", isEdit);
  domElements.qaModeBtn.classList.toggle("active", !isEdit);
}

// ファイル名から拡張子を除いたベース名を取得する関数
export function domBaseName(fileName) {
  if (!fileName.endsWith(".md")) return fileName;
  return fileName.slice(0, -3);
}

// エディタにファイルの内容をセットする関数
export function domSetEditorContent(fileName, content) {
  domElements.fileNameInput.value = domBaseName(fileName);
  domElements.editor.value = content || "";
}

// エディタの内容をクリアして新規ファイルの状態にする関数
export function domResetEditorContent() {
  domElements.fileNameInput.value = "";
  domElements.editor.value = "";
}

// ファイルリストを画面に表示する関数
export function domRenderFileList(files, currentFile, onSelectFile) {
  domElements.fileListEl.innerHTML = "";
  for (const file of files) {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.textContent = file;
    button.classList.toggle("selected", file === currentFile);
    button.addEventListener("click", () => onSelectFile(file));
    li.appendChild(button);
    domElements.fileListEl.appendChild(li);
  }
}

// 回答のテキスト出力を行う関数
export function domSetOutput(text) {
  domElements.answerOutput.classList.add("plain");
  domElements.answerOutput.textContent = text || "";
}

// 回答のMarkdown出力を行う関数
function withReferenceLinks(markdownText) {
  return (markdownText || "").replace(/\[資料(\d+)\](?!\()/g, "[資料$1](ref:$1)");
}

// 回答のMarkdown出力を行う関数
export function domSetMarkdownOutput(markdownText) {
  if (!window.marked) {
    domSetOutput(markdownText || "");
    return;
  }
  domElements.answerOutput.classList.remove("plain");
  domElements.answerOutput.innerHTML = marked.parse(withReferenceLinks(markdownText));
}

// ファイルリストをAPIから取得して画面に表示する関数
export function domBindRefLinkClick(onReferenceClick) {
  domElements.answerOutput.addEventListener("click", async (event) => {
    const link = event.target.closest('a[href^="ref:"]');
    if (!link) return;
    event.preventDefault();
    const refIndex = Number(link.getAttribute("href").slice(4));
    if (Number.isNaN(refIndex) || refIndex <= 0) return;
    await onReferenceClick(refIndex);
  });
}

// Mermaidで作図をクリアする関数
export function domClearDiagram() {
  domElements.diagramOutput.innerHTML = "";
}

// Mermaidコードを正規化して抽出する関数
function normalizeMermaidCode(rawCode) {
  const source = (rawCode || "").trim();
  const fenced = source.match(/```mermaid\s*([\s\S]*?)```/i);
  if (fenced) return fenced[1].trim();
  return source;
}

// Mermaidコードをレンダリングして画面に表示する関数
export async function domRenderMermaid(rawCode) {
  domSetMarkdownOutput('作図を行いました。');
  try {
    const mermaidCode = normalizeMermaidCode(rawCode || '');
    const renderId = `mindmap-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const rendered = await mermaid.render(renderId, mermaidCode);
    domElements.diagramOutput.innerHTML = rendered.svg;
  } catch (error) {
    console.error("Mermaid render error:", error);
    domSetOutput("Mermaidの描画に失敗しました。生成結果を確認してください。");
  }
}
