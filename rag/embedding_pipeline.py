import glob
import os
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "rag_docs"
CORPUS_DIR = Path(__file__).resolve().parent / "corpus"

def chunk_text(text: str, chunk_size: int = 400):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start+chunk_size])
        start += chunk_size
    return chunks

def main():
    client = QdrantClient(host="localhost", port=6333)

    # Use the same model for indexing and querying
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    dim = model.get_sentence_embedding_dimension()

    # Recreate collection (clean rebuild)
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        client.delete_collection(collection_name=COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    points = []
    pid = 1

    for filepath in glob.glob(str(CORPUS_DIR / "*.md")):
        with open(filepath, "r") as f:
            content = f.read()

        doc_name = os.path.basename(filepath)
        chunks = chunk_text(content)

        for idx, chunk in enumerate(chunks):
            vec = model.encode(chunk).tolist()
            payload = {
                "doc_name": doc_name,
                "chunk_id": idx,
                "text": chunk,
                "allowed_roles": ["finance", "ops"],  # tighten later
            }
            points.append(PointStruct(id=pid, vector=vec, payload=payload))
            pid += 1

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {len(points)} chunks into Qdrant collection '{COLLECTION_NAME}'")

if __name__ == "__main__":
    main()
