# server

ad-blocker-dynamic のAPIサーバー側実装を配置するディレクトリです。ブロックルールの保存と配信を担当します。

- [main.py](main.py) - サーバー起動処理
- [requirements.txt](requirements.txt) - Python依存設定
- [rules.json](rules.json) - 広告ブロックルール

実行例:

```bash
pip install -r requirements.txt
python main.py
```
