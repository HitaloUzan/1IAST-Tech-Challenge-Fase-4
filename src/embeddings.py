import os
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer


def criar_banco_vetorial():
  raiz_projeto = os.path.abspath(
      os.path.join(os.path.dirname(__file__), "..")
  )
  caminho_csv = os.path.join(
      raiz_projeto, "data", "processed", "reviews_clean.csv"
  )
  caminho_chroma = os.path.join(raiz_projeto, "data", "chroma_db")

  print("A carregar a base de dados tratada...")
  if not os.path.exists(caminho_csv):
    print(
        f"Erro: O ficheiro {caminho_csv} nao foi encontrado. Conclua o"
        " pre-processamento primeiro."
    )
    return

  df = pd.read_csv(caminho_csv)

  # Garantir que o review_score é numérico e tratar nulos
  df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce").fillna(
      3
  )

  # Vamos indexar uma amostra maior ou toda a base limpa (ex: 10000 documentos) para garantir variedade de notas baixas
  df = df.head(10000)
  print(f"Total de documentos a indexar no ChromaDB: {len(df)}")

  print(
      "A carregar o modelo de embeddings do Hugging Face"
      " (sentence-transformers)..."
  )
  modelo_embeddings = SentenceTransformer(
      "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  )

  print("A gerar os embeddings (vetores) para os comentarios...")
  textos = df["document_text"].tolist()
  ids = df["review_id"].astype(str).tolist()

  metadados = []
  for _, row in df.iterrows():
    metadados.append({
        "review_score": int(row["review_score"]),
        "product_category_name": str(row["product_category_name"]),
        "order_purchase_timestamp": str(row["order_purchase_timestamp"]),
    })

  vetores = modelo_embeddings.encode(textos, show_progress_bar=True).tolist()

  print(f"A inicializar o ChromaDB local em: {caminho_chroma}")
  cliente_chroma = chromadb.PersistentClient(path=caminho_chroma)

  nome_colecao = "olist_reviews_voc"
  try:
    cliente_chroma.delete_collection(name=nome_colecao)
  except:
    pass

  colecao = cliente_chroma.create_collection(name=nome_colecao)

  print("A inserir os vetores, textos e metadados no ChromaDB...")
  tamanho_lote = 500
  for i in range(0, len(textos), tamanho_lote):
    fim = i + tamanho_lote
    colecao.add(
        ids=ids[i:fim],
        embeddings=vetores[i:fim],
        documents=textos[i:fim],
        metadatas=metadados[i:fim],
    )

  print("Sucesso! Base vetorial recriada e populada com metadados limpos.")


if __name__ == "__main__":
  criar_banco_vetorial()