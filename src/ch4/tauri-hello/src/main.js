// 読み込みが完了したときに実行されるコード --- (※1)
window.addEventListener("DOMContentLoaded", () => {
  // 画面を書き換え
  const body = document.querySelector("body");
  body.innerHTML = `
    <div style="text-align: center;">
      <h1>Taruriで作ったサイコロ</h1>
      <div id="dice">-</div>
      <div><button id="roll">サイコロを振る</button></div>
    </div>
  `;
  const dice = document.querySelector("#dice");
  const roll = document.querySelector("#roll");
  // ボタンがクリックされたときの処理 --- (※2)
  roll.addEventListener("click", () => {
    // 1から6までの乱数を生成
    const value = Math.floor(Math.random() * 6) + 1;
    // サイコロの目を表示
    dice.textContent = value;
  });
  dice.style.padding = "100px"; // サイコロのスタイルを変更
  dice.style.fontSize = "170px";
});
