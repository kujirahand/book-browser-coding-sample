# fact_checker

主張文を入力してファクトチェックを行うFastAPIアプリです。UIは static ディレクトリのファイルを利用します。

- [main.py](main.py) - サーバー起動処理
- [llm_factchecker.py](llm_factchecker.py) - 判定処理
- [llm_prompt.py](llm_prompt.py) - プロンプト生成
- [requirements.txt](requirements.txt) - 依存ライブラリ
- [static](static/) - フロントエンド

実行例:

```bash
pip install -r requirements.txt
python main.py
```
