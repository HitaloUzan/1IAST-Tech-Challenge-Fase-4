import os
import pandas as pd


def carregar_e_limpar_dados():
  raiz_projeto = os.path.abspath(
      os.path.join(os.path.dirname(__file__), "..")
  )
  caminho_raw = os.path.join(raiz_projeto, "data", "raw")
  caminho_processed = os.path.join(raiz_projeto, "data", "processed")

  print(f"Caminho absoluto RAW: {caminho_raw}")
  print(f"Caminho absoluto PROCESSED: {caminho_processed}")

  print("A carregar os 4 datasets da Olist...")

  try:
    reviews = pd.read_csv(
        os.path.join(caminho_raw, "olist_order_reviews_dataset.csv")
    )
    orders = pd.read_csv(os.path.join(caminho_raw, "olist_orders_dataset.csv"))
    order_items = pd.read_csv(
        os.path.join(caminho_raw, "olist_order_items_dataset.csv")
    )
    products = pd.read_csv(
        os.path.join(caminho_raw, "olist_products_dataset.csv")
    )
  except FileNotFoundError as e:
    print(f"Erro ao encontrar os ficheiros em data/raw/: {e}")
    return None

  print("A limpar e a tratar valores ausentes...")
  reviews_com_texto = reviews.dropna(subset=["review_comment_message"]).copy()
  reviews_com_texto["review_comment_message"] = (
      reviews_com_texto["review_comment_message"]
      .astype(str)
      .str.replace("\n", " ")
      .str.replace("\r", " ")
      .str.strip()
  )
  reviews_com_texto = reviews_com_texto[
      reviews_com_texto["review_comment_message"] != ""
  ]

  print("A cruzar dados (Reviews -> Orders -> Items -> Products)...")

  # Cruzamentos sucessivos para ligar o review à categoria do produto
  df_aux = reviews_com_texto.merge(
      orders[["order_id", "order_purchase_timestamp"]],
      on="order_id",
      how="inner",
  )
  df_aux = df_aux.merge(
      order_items[["order_id", "product_id"]], on="order_id", how="inner"
  )
  df_enriquecido = df_aux.merge(
      products[["product_id", "product_category_name"]],
      on="product_id",
      how="left",
  )

  df_enriquecido["product_category_name"] = df_enriquecido[
      "product_category_name"
  ].fillna("desconhecido")
  df_enriquecido = df_enriquecido.drop_duplicates(subset=["review_id"])

  print(f"Total de registos após cruzamento completo: {len(df_enriquecido)}")

  print("A formatar os documentos estruturados para o RAG...")

  def construir_documento_texto(row):
    return (
        f"[Metadados] Categoria do Produto: {row['product_category_name']} | "
        f"Nota da Avaliação: {row['review_score']}/5 | "
        f"Data da Compra: {row['order_purchase_timestamp']}\n"
        f"[Comentário do Cliente]: {row['review_comment_message']}"
    )

  df_enriquecido["document_text"] = df_enriquecido.apply(
      construir_documento_texto, axis=1
  )

  df_final = df_enriquecido[[
      "review_id",
      "order_id",
      "product_id",
      "product_category_name",
      "review_score",
      "order_purchase_timestamp",
      "review_comment_message",
      "document_text",
  ]]

  os.makedirs(caminho_processed, exist_ok=True)
  caminho_arquivo_saida = os.path.join(caminho_processed, "reviews_clean.csv")
  df_final.to_csv(caminho_arquivo_saida, index=False, encoding="utf-8")

  print(f"Ficheiro guardado com sucesso em: {caminho_arquivo_saida}")
  return df_final


if __name__ == "__main__":
  carregar_e_limpar_dados()