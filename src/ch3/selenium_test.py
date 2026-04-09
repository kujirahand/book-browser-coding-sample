import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 対象URLを指定
target_url = "https://kujirahand.com"

# ヘッドレス（画面を表示しない）設定
options = Options()
options.add_argument("--headless")

# ブラウザを起動 --- (*1)
driver = webdriver.Chrome(options=options)
try:
    # 対象のWebページを開く --- (*2)
    driver.get(target_url)
    time.sleep(2)  # 確実に読むためにページ読込を待つ --- (*3)
    # タイトル取得 --- (*4)
    title = driver.title
    print("タイトル:", title)
    # h1タグ取得
    h1_elements = driver.find_elements(By.TAG_NAME, "h1")
    if h1_elements:
        print("見出し:", h1_elements[0].text)
finally:
    # ブラウザ終了
    driver.quit()

