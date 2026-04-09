"""データ抽出処理"""

def extract_sales_from_page(page):
    """現在のページから売り上げデータを抽出"""
    sales = []
    # table要素から行を取得 --- (※1)
    rows = page.query_selector_all('table tr')
    for row in rows[1:]:  # ヘッダー行をスキップ --- (※2)
        cells = row.query_selector_all('td')
        if len(cells) >= 8:
            # 取得したデータを結果に追加 --- (※3)
            sale = {
                '取引ID': cells[0].inner_text().strip(),
                '日時': cells[1].inner_text().strip(),
                '商品ID': cells[2].inner_text().strip(),
                '商品名': cells[3].inner_text().strip(),
                '単価': cells[4].inner_text().strip(),
                '数量': cells[5].inner_text().strip(),
                '小計': cells[6].inner_text().strip(),
                '支払い方法': cells[7].inner_text().strip(),
            }
            sales.append(sale)
    return sales
