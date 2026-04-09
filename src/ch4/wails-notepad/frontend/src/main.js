import './style.css';
import './app.css';
// Go言語側で定義したメソッドSaveとLoadをインポート --- (※1)
import {Save, Load} from '../wailsjs/go/main/App';
// HTMLの内容を定義 --- (※2)
document.querySelector('#app').innerHTML = `
    <div id="buttons">
        <button id="save">保存</button>
        <button id="load">読込</button>
    </div>
    <div id="text_block">
        <textarea id="text"></textarea>
    </div>
`;
// ボタンとテキストエリアの要素を取得 --- (※3)
const saveButton = document.querySelector('#save');
const loadButton = document.querySelector('#load');
const textArea = document.querySelector('#text');
// 保存ボタンのクリックイベントを定義 --- (※4)
saveButton.addEventListener('click', async () => {
    const text = textArea.value;
    try {
        const filename = await Save(text);
        if (!filename) return;
        alert(`ファイルを保存しました: ${filename}`);
    } catch (err) {
        alert(`保存に失敗: ${err}`);
    }
});
// 読み込みボタンのクリックイベントを定義 --- (※5)
loadButton.addEventListener('click', async () => {
    try {
        const content = await Load();
        if (!content) return;
        textArea.value = content;
        alert('ファイルを読み込みました');
    } catch (err) {
        alert(`読み込みに失敗: ${err}`);
    }
});
