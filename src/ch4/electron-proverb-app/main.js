// Electrionのメインプロセス
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");

// ブラウザウィンドウを作成する関数
function createWindow() {
  const win = new BrowserWindow({
    width: 640,
    height: 400,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // index.htmlをロード
  win.loadFile("index.html");
}
// アプリが準備できたらウィンドウを作成
app.whenReady().then(createWindow);
// macOSで全てのウィンドウが閉じられたときの挙動
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
// macOSでアプリがアクティブになったときの挙動
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
// レンダリングプロセスから呼び出せるAPIを定義 --- (※1)
ipcMain.handle("getProverb", (event) => {
  // ここで何らかの処理を行って結果を返す
  const textFile = path.join(__dirname, "proverb.txt");
  // ファイルの内容を読み込む
  return fs.readFileSync(textFile, "utf-8");
});

