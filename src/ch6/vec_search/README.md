# vec_search

ベクトル検索とRAG回答を組み合わせたFlaskアプリです。検索インデックス、静的画面、RAGサーバーをまとめています。

- [rag_server.py](rag_server.py) - RAGサーバー本体
- [search_server.py](search_server.py) - 検索処理
- [create_index.py](create_index.py) - インデックス作成
- [dataset_to_text.py](dataset_to_text.py) - データ整形
- [requirements.txt](requirements.txt) - 依存ライブラリ
- [data](data/) - 検索インデックス
- [static](static/) - フロントエンド

実行例:

```bash
pip install -r requirements.txt
python rag_server.py
```
