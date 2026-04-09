# 第7章のプログラム概要

この章では、ローカルLLMやベクトル検索を活用した実用アプリを扱います。単体のAI呼び出しテストから、ノート、作図、アイデア整理といった実践的なアプリへ発展させています。

## 含まれるプログラム

- [ollama_test.py](ollama_test.py): Ollamaで起動したローカルLLMへ問い合わせを送る基本テストです。
- [ollama_embedding_test.py](ollama_embedding_test.py): OllamaのEmbedding機能を使ってベクトルを生成するサンプルです。
- [ainote](ainote/): ノート保存、検索、要約、作図支援をまとめたAIノートアプリです。
- [diagram-agent](diagram-agent/): 指示からMermaid図を生成する作図支援アプリです。
- [idea-bank](idea-bank/): ブラウザで選択した文章を保存し、AIでタグや要約を付けるアイデア管理アプリです。

## 学べること

- Ollamaを使ったローカルLLM利用
- Embeddingを使ったAI検索機能
- Flaskベースの実用アプリ構成
- ブラウザ拡張とAIサーバーの連携

## 実行例

Ollamaを起動した状態で、単体スクリプトを次のように試せます。

```bash
cd src/ch7
python ollama_test.py
python ollama_embedding_test.py
```

`ainote` や `diagram-agent` は、各フォルダで依存関係を入れたうえでPythonアプリを起動します。例として `ainote` は次のように実行します。

```bash
cd src/ch7/ainote
pip install -r requirements.txt
python app.py
```

`idea-bank` はサーバー起動に加えて、`extension/` フォルダをChromeへ読み込んで使います。
