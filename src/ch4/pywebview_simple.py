import webview

# HTMLを直接コード内に記述
html = """
<div style="text-align: center; margin-top: 150px;">
<h1>格言</h1>
<p style="font-size:32px">
    心配事があると心が沈み<br>良い言葉によって心が晴れる</p>
</div>
"""
# pywebviewでウィンドウを作成し、HTMLを表示
window = webview.create_window("HelloApp", html=html)
webview.start()
