"""Loads the ChromaDB collection, building it from the stored embeddings when needed.

The collection uses cosine distance (0 = same meaning, 2 = opposite), which
gives the similarity threshold in src/retriever.py a known, model-independent
scale. Everything that is not the review text goes to metadata so it can be
used in ``where`` filters at query time.
"""

import chromadb
import numpy as np
import pandas as pd

from src.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_IDS_FILE,
    EMBEDDINGS_FILE,
    REVIEWS_CSV,
)

BATCH_SIZE = 2000


def build_metadata(row) -> dict:
  metadata = {
      "review_id": str(row.review_id),
      "order_id": str(row.order_id),
      "review_score": int(row.review_score),
      "product_category_name": str(row.product_category_name),
      "order_purchase_timestamp": str(row.order_purchase_timestamp),
      "purchase_month": str(row.purchase_month),
      "delivery_status": str(row.delivery_status),
      "is_short": bool(row.is_short),
  }
  if pd.notna(row.purchase_year):
    metadata["purchase_year"] = int(row.purchase_year)
  if pd.notna(row.delivery_delay_days):
    metadata["delivery_delay_days"] = int(row.delivery_delay_days)
  return metadata


def build_collection(client) -> chromadb.Collection:
  df = pd.read_csv(REVIEWS_CSV)
  vectors = np.load(EMBEDDINGS_FILE).astype(np.float32)
  with open(EMBEDDING_IDS_FILE, encoding="utf-8") as f:
    ids = f.read().split("\n")
  if ids != df["review_id"].astype(str).tolist():
    raise ValueError(
        "Os embeddings não correspondem à base atual. Rode: python -m src.embeddings"
    )

  try:
    client.delete_collection(COLLECTION_NAME)
  except Exception:
    pass
  collection = client.create_collection(
      name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
  )

  documents = df["review_text"].tolist()
  metadatas = [build_metadata(row) for row in df.itertuples(index=False)]
  for start in range(0, len(ids), BATCH_SIZE):
    end = start + BATCH_SIZE
    collection.add(
        ids=ids[start:end],
        embeddings=vectors[start:end],
        documents=documents[start:end],
        metadatas=metadatas[start:end],
    )
  return collection


def get_collection(path: str = CHROMA_DIR) -> chromadb.Collection:
  client = chromadb.PersistentClient(path=path)
  expected = len(np.load(EMBEDDINGS_FILE, mmap_mode="r"))
  try:
    collection = client.get_collection(COLLECTION_NAME)
    if collection.count() == expected:
      return collection
  except Exception:
    pass
  print("Construindo a coleção no ChromaDB a partir dos embeddings salvos...")
  return build_collection(client)


if __name__ == "__main__":
  print(f"Documentos indexados: {get_collection().count()}")
