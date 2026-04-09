// モジュールをインポート --- (*1)
import {
  apiAsk, apiDiagram, apiGetFile, apiGetFiles, apiSave, apiSummarize
} from "./api.js";
import {
  domBindRefLinkClick, domElements, domInitRenderers,
  domRenderFileList, domResetEditorContent, domSetEditorContent,
  domSetMarkdownOutput, domSetMode, domSetOutput, domRenderMermaid
} from "./dom.js";
// 現在の状態を管理する変数を定義 --- (*2)
let currentMode = "edit"; // 表示画面 "edit" または "question" を保持
let currentFile = ""; // 現在編集注のファイル名
let referenceFiles = []; // 資料リンクに対応するファイル名のリスト
// アプリケーションの初期化処理 --- (*3)
function initializeApp() {
  domInitRenderers(); // Mermaidとmarkedの初期化
  bindEvents(); // イベントのバインド
  loadFiles(); // ファイルリストの読み込みと表示
}
// 画面上の要素とイベントをバインド --- (*4)
function bindEvents() {
  const el = domElements;
  el.editModeBtn.addEventListener("click", () => switchMode("edit"));
  el.qaModeBtn.addEventListener("click", () => switchMode("question"));
  el.newFileBtn.addEventListener("click", resetEditor);
  el.saveBtn.addEventListener("click", saveFile);
  el.askBtn.addEventListener("click", askQuestion);
  el.summarizeBtn.addEventListener("click", summarizeText);
  el.drawBtn.addEventListener("click", generateDiagram);
  domBindRefLinkClick(openReferenceFile);
}
// 画面のモード切替の関数
function switchMode(mode) { currentMode = mode; domSetMode(mode); }
// ファイルリストの読み込みと表示を行う関数 --- (*5)
async function loadFiles() {
  const res = await apiGetFiles();
  const files = Array.isArray(res.data.files) ? res.data.files : [];
  domRenderFileList(files, currentFile, openFile);
}
// ファイルを開いてエディタに内容を表示する関数 --- (*6)
async function openFile(fileName) {
  currentFile = fileName;
  const result = await apiGetFile(fileName);
  if (!result.ok) { alert("ファイルの読み込みに失敗しました。"); return; }
  domSetEditorContent(fileName, result.data.content);
  await loadFiles();
  if (currentMode !== "edit") switchMode("edit");
}
// エディタをリセットして新規ファイルの状態にする --- (*7)
function resetEditor() {
  currentFile = "";
  domResetEditorContent();
  loadFiles();
}
// 資料リンクをクリックしたときに対応するファイルを開く関数
async function openReferenceFile(refIndex) {
  const fileName = referenceFiles[refIndex - 1];
  if (!fileName) return;
  await openFile(fileName);
  switchMode("edit");
}
// ファイルを保存する関数 --- (*8)
async function saveFile() {
  const fileName = domElements.fileNameInput.value.trim();
  if (!fileName) { alert("保存にはファイル名が必要です。"); return; }
  const payload = { file_name: fileName, old_file_name: currentFile,
                    content: domElements.editor.value};
  const result = await apiSave(payload);
  if (!result.ok) { alert(result.data.error || "保存失敗"); return; }
  currentFile = result.data.file || `${fileName}.md`;
  await loadFiles(); // ファイルリストを更新
}
// 質問を送信して回答を表示する関数 --- (*9)
async function askQuestion() {
  const question = domElements.questionInput.value.trim();
  if (!question) { return; }
  domSetOutput("回答を生成中です...");
  const res = await apiAsk(question);
  if (!res.ok) {
    domSetOutput(res.data.error || "質問に失敗しました。"); return;
  }
  referenceFiles = (res.data.contexts || []).map((item) => item.file);
  domSetMarkdownOutput(res.data.answer || "");
  await loadFiles();
}
// テキストを要約して表示する関数 --- (*10)
async function summarizeText() {
  const focus = domElements.questionInput.value.trim();
  domSetOutput("要約を生成中です...");
  const result = await apiSummarize(focus);
  if (!result.ok) {
    domSetOutput(result.data.error || "要約に失敗しました。");
    return;
  }
  referenceFiles = (result.data.summaries || [])
    .map((item) => item.source_file || item.summary_file);
  domSetMarkdownOutput(result.data.display_text || "");
  await loadFiles();
}
// 作図を生成して表示する関数 --- (*11)
async function generateDiagram() {
  const focus = domElements.questionInput.value.trim();
  domSetOutput("作図を生成中です...");
  const result = await apiDiagram({focus});
  if (!result.ok) { alert(result.data.error || "作図失敗"); return; }
  await domRenderMermaid(result.data.mermaid); // Mermaid図をレンダリング
}
initializeApp(); // アプリケーションの初期化関数
