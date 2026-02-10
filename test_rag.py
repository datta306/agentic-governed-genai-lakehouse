import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.rag_retriever import retrieve_docs

results = retrieve_docs(
    "What are common causes of revenue drop and how to check late ingestion?",
    user_role="finance",
    top_k=3
)

print("RAG Results:")
for r in results:
    print(f"\nSource: {r['doc_name']} (chunk {r['chunk_id']})")
    print(r["text"])
