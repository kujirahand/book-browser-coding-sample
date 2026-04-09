import './style.css';
// Goの関数をJSから呼び出すためのインポート --- (*1)
import {OpenSaveDialog, SaveB64Image, GenImage} from '../wailsjs/go/main/App';
// UIの初期化 --- (*2)
document.querySelector('#app').innerHTML = `
    <h3>「フラクタル画像作成ツール」画面クリックで中心点をズームします</h3>
    <div><canvas id="cv" width="600" height="600"></canvas></div>
    <div id="status" style="font-size:12px;"></div>
    <div id="buttons"><button id="save-btn">画像を保存</button></div>
`;
// キャンバスとボタンの要素を取得 --- (*3)
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
const saveBtn = document.getElementById('save-btn');
const statusEl = document.getElementById('status');
// ボタンの見た目を調整 --- (*4)
saveBtn.style.fontSize = '20px'; // ボタンフォントを大きくする
saveBtn.style.width = '500px'; // ボタンのサイズを大きくする
// デフォルトの中心点とズームレベルを設定 --- (*5)
let cx = 0.3383;
let cy = -0.5702;
let zoom = 16000.0;
const maxIter = 500;
const zoomFactor = 1.5;
let currentImageData = '';
// マンデルブロ集合の画像を生成してキャンバスに描画する関数 --- (*6)
async function drawImage() {
    // Goの関数を呼び出して画像を生成 --- (*6)
    const b64data = await GenImage(cx, cy, zoom, maxIter);
    currentImageData = b64data;
    // 生成された画像をキャンバスに描画 --- (*7)
    const img = new Image();
    img.onload = () => { ctx.drawImage(img, 0, 0) };
    img.src = b64data;
    updateStatus();
}
// キャンバスをクリックしたときのイベント --- (*8)
cv.addEventListener('mousedown', async (event) => {
    const rect = cv.getBoundingClientRect(); // クリックした位置を得る
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    // クリック位置を複素数平面の座標に変換 --- (*9)
    const nextCx = (x - cv.width / 2) / (0.5 * zoom * cv.width) + cx;
    const nextCy = (y - cv.height / 2) / (0.5 * zoom * cv.height) + cy;
    cx = nextCx;
    cy = nextCy;
    zoom *= zoomFactor;
    await drawImage();
});
// 保存ボタンがクリックされたときのイベント --- (*10)
saveBtn.addEventListener('click', async () => {
    try {
        // 保存ダイアログを開いてファイル名を取得 --- (*11)
        const filename = await OpenSaveDialog();
        if (filename) {
            // ファイルに画像データを保存 --- (*12)
            await SaveB64Image(currentImageData, filename);
            console.log('Saved image:', filename);
        }
    } catch (error) {
        console.error('Error opening save dialog:', error);
    }
});
// ページが読み込まれたときにマンデルブロ集合の画像を生成して描画 --- (*13)
drawImage().catch((error) => {
    console.error('Failed to draw initial image:', error);
});
// ステータス表示を更新する関数 --- (*14)
function updateStatus() {
    statusEl.textContent = `(${cx.toFixed(4)}, ${cy.toFixed(4)})` +
        ` zoom: ${zoom.toFixed(1)}`;
}
