"""ストレージ処理（CSV保存）"""
import csv
from config import CSV_FIELDNAMES

def save_to_csv(sales_data, filename):
    """売り上げデータをCSVファイルに保存"""
    if not sales_data:
        print(f"  警告: {filename} に保存するデータがありません")
        return
    # CSVファイルに保存 --- (※1)
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for sale in sales_data:
            writer.writerow(sale)
