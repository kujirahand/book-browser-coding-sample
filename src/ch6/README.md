# 第6章のプログラム概要

この章では、ローカルAPIサーバーとAI機能を組み合わせたアプリの基礎を学びます。LLM呼び出し、ベクトル検索、RAG、ファクトチェックといったAIアプリの中核要素を扱います。

## 含まれるプログラム

- `llm_hello.py`: LiteLLM経由で複数のLLMを同じ書き方で呼び出すサンプルです。
- `vec_test.py`: 文章をベクトル化して類似度順に並べる基本的なベクトル検索の例です。
- `fact_checker/`: 入力された主張に対してファクトチェックを行うFastAPIアプリです。
- `vec_search/`: ベクトル検索とLLM回答を組み合わせたRAGサーバーのサンプルです。

## 学べること

- LLM APIの統一的な呼び出し方
- 文章埋め込みと類似度検索
- FastAPIやFlaskでのAI向けAPI実装
- 検索結果を根拠に回答するRAGの基本構成

## 実行例

単体スクリプトは次のように実行します。

```bash
cd src/ch6
python llm_hello.py
python vec_test.py
```

ファクトチェッカーは次のように起動します。

```bash
cd src/ch6/fact_checker
python main.py
```

RAGサーバーは次のように起動します。

```bash
cd src/ch6/vec_search
python rag_server.py
```

実行にはAPIキーやモデルの事前準備が必要なものがあります。
