import webview

# HTML/JavaScriptを直接コード内に記述
html = """
<style>
  h1 { background-color: blue; color: white;}
  .box { text-align: center; }
  #disp { font-size: 120px; }
  button { font-size: 48px; }
</style>
<div class="box">
  <h1>サイコロ</h1>
  <p id="disp">?</p>
  <button onclick="rollDice()">サイコロを振る</button>
</div>
<script>
function rollDice() {
  const r = Math.floor(Math.random() * 6) + 1;
  document.getElementById('disp').textContent = r;
}
</script>
"""
# pywebviewでウィンドウを作成し、HTMLを表示
window = webview.create_window("サイコロ", html=html)
webview.start()
