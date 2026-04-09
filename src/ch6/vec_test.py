"""文章を類似している順に並べるベクトル検索の例"""
from sentence_transformers import SentenceTransformer
import numpy as np

# 検索元の文章 --- (*1)
source = "リンゴはとても美味しい果物です。"
# ベクトル検索の対象となる文章 --- (*2)
targets = [
    "爽やかな朝、今日も良い仕事ができそうだ。",
    "PythonはAIにとって美味しいプログラミング言語です。",
    "健康の秘訣はよく笑うこと、喜びこそ治療薬です。",
    "ミカンって本当に美味しいですよね！",
    "リンゴは味覚を刺激するので多くの人に愛されている。",
    "Do you like apples? Yes, I like them very much!",
]
# ベクトル検索の準備とモデルのダウンロード --- (*3)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# ベクトルの生成 --- (*4)
source_vec = model.encode(source)
target_vecs = model.encode(targets)
# コサイン類似度の計算関数を定義 --- (*5)
def cosine_similarity(a, b):
    a_norm = np.linalg.norm(a)
    b_norms = np.linalg.norm(b, axis=1)
    return np.dot(b, a) / (a_norm * b_norms)
# コサイン類似度の計算 --- (*6)
similarities = cosine_similarity(source_vec, target_vecs)
# 結果の表示 --- (*7)
print("元となる文:", source)
results = sorted(zip(targets, similarities), key=lambda x: x[1], reverse=True)
for target, similarity in results:
    print(f"類似度: {similarity:.4f} - {target}")
