import os
import json

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


# =========================
# 1. 加载 Embedding 模型
# =========================

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


# =========================
# 2. 文本分块
# =========================


def chunk_text(text, chunk_size=500, overlap=100):
    paragraphs = [
        paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()
    ]

    chunks = []

    current_chunk = ""

    for paragraph in paragraphs:
        if not current_chunk:
            current_chunk = paragraph

            continue

        candidate = current_chunk + "\n\n" + paragraph

        if len(candidate) <= chunk_size:
            current_chunk = candidate

        else:
            chunks.append(current_chunk)

            overlap_text = current_chunk[-overlap:]

            current_chunk = overlap_text + "\n\n" + paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# =========================
# 3. 加载知识库
# =========================


def load_knowledge():
    chunks = []

    knowledge_dir = "knowledge"

    for filename in os.listdir(knowledge_dir):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(knowledge_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        parts = chunk_text(content, chunk_size=500, overlap=100)

        for part in parts:
            chunks.append({"content": part, "source": filename})

    return chunks


# =========================
# 4. 创建知识库
# =========================

knowledge_chunks = []

index = None

FAISS_DIR = "faiss_db"

INDEX_PATH = os.path.join(FAISS_DIR, "knowledge.index")

METADATA_PATH = os.path.join(FAISS_DIR, "metadata.json")


def save_faiss():
    if index is None:
        return

    os.makedirs(FAISS_DIR, exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(knowledge_chunks, f, ensure_ascii=False, indent=2)

    print("FAISS 索引保存成功")


def load_faiss():
    global knowledge_chunks
    global index

    if not os.path.exists(INDEX_PATH):
        return False

    if not os.path.exists(METADATA_PATH):
        return False

    print("发现已有 FAISS 索引，开始加载...")

    index = faiss.read_index(INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        knowledge_chunks = json.load(f)

    print(f"FAISS 索引加载成功，共 {len(knowledge_chunks)} 个知识块")

    print(f"FAISS 向量数量：{index.ntotal}")

    return True


def reload_knowledge():
    global knowledge_chunks
    global index

    print("开始重新加载知识库...")

    knowledge_chunks = load_knowledge()

    texts = [item["content"] for item in knowledge_chunks]

    if not texts:
        index = None

        print("知识库为空")

        return

    # =========================
    # 5. 计算 Embedding
    # =========================

    embeddings = model.encode(texts)

    embeddings = np.array(embeddings).astype("float32")

    # =========================
    # 6. 创建 FAISS 索引
    # =========================

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    print(f"知识库重新加载完成，共 {len(knowledge_chunks)} 个知识块")

    print(f"FAISS 向量数量：{index.ntotal}")
    save_faiss()


# =========================
# 7. 搜索知识库
# =========================


def search_knowledge(question, top_k=3, threshold=0.5):
    if index is None or not knowledge_chunks:
        return []

    # 问题 Embedding

    question_embedding = model.encode([question])

    question_embedding = np.array(question_embedding).astype("float32")

    # 归一化

    faiss.normalize_L2(question_embedding)

    # FAISS 搜索

    scores, indices = index.search(question_embedding, top_k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue

        if score < threshold:
            continue

        item = knowledge_chunks[idx]

        results.append(
            {
                "score": float(score),
                "content": item["content"],
                "source": item["source"],
            }
        )

    return results


# =========================
# 8. 启动时加载知识库
# =========================

if not load_faiss():
    reload_knowledge()


# =========================
# 9. 单独测试
# =========================

if __name__ == "__main__":
    question = input("请输入问题：")

    results = search_knowledge(question)

    print("\nFAISS 检索结果：")

    for item in results:
        print(f"[相似度：{item['score']:.4f}]")

        print(f"[来源：{item['source']}]")

        print(item["content"])

        print()
