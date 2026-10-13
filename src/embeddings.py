import os
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer


def criar_banco_vetorial():
  # Obter o caminho absoluto da raiz do projeto
  raiz_projeto = os.path.abspath(
      os.path.join(os.path.dirname(__file__), "..")
  )
  caminho_csv = os.path.join(raiz_projeto, "data", "processed", "reviews_clean.csv")
  caminho_chroma = os.path.join(raiz_projeto, "data", "chroma_db")

  print("A carregar a base de dados tratada...")
  if not os.path.exists(caminho_csv):
    print(
        f"Erro: O ficheiro {caminho_csv} não foi encontrado. Conclua o Passo 2"
        " primeiro."
    )
    return

  df = pd.read_csv(caminho_csv)

  # Limitar a 5000 reviews para teste inicial (pode remover se quiser indexar tudo)
  df = df.head(5000)
  print(f"Total de documentos a indexar no ChromaDB: {len(df)}")

  print(
      "A carregar o modelo gratuito de embeddings do Hugging Face"
      " (sentence-transformers)..."
  )
  modelo_embeddings = SentenceTransformer(
      "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  )

  print("A gerar os embeddings (vetores) para os comentários...")
  textos = df["document_text"].tolist()
  ids = df["review_id"].astype(str).tolist()

  # Metadados ajustados com base nas colunas reais disponíveis no CSV processado
  metadados = []
  for _, row in df.iterrows():
    metadados.append({
        "review_score": int(row["review_score"]),
        "order_purchase_timestamp": str(row["order_purchase_timestamp"]),
    })

  # Gerar os vetores numéricos através do modelo local
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

  print(
      "Sucesso! Base de dados vetorial criada e populada localmente sem"
      " custos."
  )


if __name__ == "__main__":
  criar_banco_vetorial()