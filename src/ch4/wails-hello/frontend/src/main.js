import './style.css'; // --- (※1)

// メインのUI(HTML)を指定 --- (※2)
document.querySelector('#app').innerHTML = `
    <h1>Wailsで作ったサイコロ</h1>
    <div id="msg"></div>
    <div><button id="d-btn">サイコロを振る</button></div>
`;
// ボタンをクリックしたときの処理 --- (※3)
const msg = document.querySelector('#msg');
const d_btn = document.querySelector('#d-btn')
d_btn.addEventListener('click', () => {
    const r = Math.floor(Math.random() * 6) + 1; // 乱数を生成
    msg.textContent = r
})
// 文字サイズを変更
d_btn.style.fontSize = '30px';
msg.style.fontSize = '100px';
