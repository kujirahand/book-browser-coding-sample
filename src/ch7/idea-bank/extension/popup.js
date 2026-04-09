// サーバーの管理画面を開くためのコード
const SERVER_URL = "http://127.0.0.1:8000/";
// サーバーの管理画面を開く関数を定義
async function openServer() {
  await chrome.tabs.create({ url: SERVER_URL });
}
const openBtn = document.getElementById("openBtn")
openBtn.addEventListener("click", openServer);
openServer();
