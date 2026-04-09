// Electrionのメインプロセス
const { app, BrowserWindow } = require("electron");

// ブラウザウィンドウを作成する関数 --- (※1)
function createWindow() {
  const win = new BrowserWindow({
    width: 640,
    height: 400,
  });
  // index.htmlをロード
  win.loadFile("index.html");
}
// アプリが準備できたらウィンドウを作成 --- (※2)
app.whenReady().then(createWindow);

// macOSで全てのウィンドウが閉じられたときの挙動 --- (※3)
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
