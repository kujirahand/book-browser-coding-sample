// 格言のデータセット --- (*1)
const quotes = [
  "水が顔を映すように人の心は他の人の心を映す",
  "受ける​より​与える​方​が​幸福​で​ある",
  "人からしてほしいと思うことは全て人にもしなければなりません",
  "相談によって計画は成功する",
  "言葉が多ければ失敗を避けられない",
];

// ページが読み込まれたとき、ランダムな格言を表示 --- (*2)
document.addEventListener('DOMContentLoaded', () => {
  displayRandomQuote();
});

// ランダムな格言を表示する関数 --- (*3)
function displayRandomQuote() {
  const idx = Math.floor(Math.random() * quotes.length);
  const quote = quotes[idx];
  document.getElementById('msg').textContent = quote;
}
