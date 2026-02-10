import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "rag_docs"

client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def retrieve_docs(query: str, user_role: str, top_k: int = 3):
    qvec = model.encode(query).tolist()

    # ✅ This qdrant-client expects the vector in `query=...` (not query_vector)
    resp = client.query_points(
        collection_name=COLLECTION_NAME,
        query=qvec,
        limit=top_k,
        with_payload=True,
    )

    results = []
    for p in resp.points:
        payload = p.payload or {}
        allowed_roles = payload.get("allowed_roles", [])
        if user_role in allowed_roles:
            results.append({
                "doc_name": payload.get("doc_name"),
                "chunk_id": payload.get("chunk_id"),
                "text": payload.get("text"),
                "score": float(p.score) if p.score is not None else None
            })

    return results
