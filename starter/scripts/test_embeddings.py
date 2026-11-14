import os
import sys
from pathlib import Path
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sentence_transformers import SentenceTransformer
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

model = SentenceTransformer("google/embeddinggemma-2", device=device)
dim = model.get_sentence_embedding_dimension()
print(f"Model dimension: {dim}")

# Test document embedding
doc_prefix = "title: none | text: "
docs = [doc_prefix + "RAG kết hợp truy xuất thông tin với mô hình ngôn ngữ lớn."]
doc_vecs = model.encode(docs, normalize_embeddings=True)
print("Doc vector shape:", doc_vecs.shape, "Norm:", (doc_vecs[0]**2).sum())

# Test query embedding
query_prefix = "task: question answering | query: "
q = query_prefix + "RAG là gì?"
q_vec = model.encode([q], normalize_embeddings=True)[0]
print("Query vector shape:", q_vec.shape, "Norm:", (q_vec**2).sum())

# Cosine similarity
similarity = float(doc_vecs[0] @ q_vec)
print(f"Cosine similarity: {similarity:.4f}")
