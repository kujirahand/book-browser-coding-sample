# server

idea-bank のサーバー側実装を配置するディレクトリです。保存、要約、タグ付けなどのAI処理を担当します。

- [app.py](app.py) - サーバー起動処理
- [llm.py](llm.py) - LLM呼び出し
- [llm_prompt.py](llm_prompt.py) - プロンプト生成
- [storage.py](storage.py) - 保存処理
- [requirements.txt](requirements.txt) - 依存ライブラリ
- [ideas](ideas/) - 保存済みアイデア
- [static](static/) - 管理画面の静的ファイル

実行例:

```bash
pip install -r requirements.txt
python app.py
```
