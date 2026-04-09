// Tauriを使うためのインポート --- (※1)
const { invoke } = window.__TAURI__.core;
// コンテンツを読み込んだときに実行する処理
window.addEventListener("DOMContentLoaded", async () => {
  // HTMLを動的に生成して、画面に表示 --- (※2)
  document.querySelector("body").innerHTML = `
    <div style="text-align: center;">
      <h1>Tauriでファイルを読み込んで表示</h1>
      <div id="outer_text">
        <textarea id="ta">???</textarea>
      </div>
    </div>`;
  // Rust側の関数を呼び出してファイルの内容を取得 --- (※3)
  const text = await invoke("read_file",
    {filename: "sample.txt"});
  // 画面に表示 --- (※4)
  const ta = document.querySelector("#ta");
  ta.value = text;
  ta.style.width = "700px";
  ta.style.height = "450px";
  ta.style.fontSize = "24px";
});
