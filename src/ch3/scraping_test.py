import requests
from bs4 import BeautifulSoup

# スクレイピング対象URLを指定
target_url = "https://kujirahand.com"

# requestsでページHTMLを取得 --- (*1)
response = requests.get(target_url)
response.raise_for_status()  # HTTPエラーがあれば例外を投げる

# BeautifulSoupでHTMLを解析 --- (*2)
soup = BeautifulSoup(response.text, "html.parser")

# タイトルを取得 --- (*3)
title = soup.title.string if soup.title else "(no title)"
print("タイトル:", title)
# h1要素を探してそのテキストを表示
h1 = soup.find("h1")
print("見出し:", h1.get_text(strip=True))
