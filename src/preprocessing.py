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

  print("A carregar os datasets disponíveis...")

  try:
    reviews = pd.read_csv(os.path.join(caminho_raw, "olist_order_reviews_dataset.csv"))
    orders = pd.read_csv(os.path.join(caminho_raw, "olist_orders_dataset.csv"))
    # A tabela de products não será usada diretamente aqui para evitar erro de chave externa sem a tabela de itens
  except FileNotFoundError as e:
    print(f"Erro ao encontrar os ficheiros: {e}")
    return None

  print("A limpar e a tratar valores ausentes...")

  # Filtrar apenas reviews que possuem mensagem de comentário textual
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

  print(f"Total de reviews com texto encontrados: {len(reviews_com_texto)}")

  print("A cruzar dados com os pedidos...")

  # Cruzamento entre reviews e orders para buscar a data da compra e status do pedido
  df_enriquecido = reviews_com_texto.merge(
      orders[[
          "order_id",
          "order_purchase_timestamp",
          "order_approved_at",
          "order_delivered_customer_date",
      ]],
      on="order_id",
      how="inner",
  )
  df_enriquecido = df_enriquecido.drop_duplicates(subset=["review_id"])

  print("A formatar os documentos estruturados para o RAG...")

  def construir_documento_texto(row):
    return (
        f"[Metadados] Nota da Avaliação: {row['review_score']}/5 | Data da"
        f" Compra: {row['order_purchase_timestamp']}\n[Comentário do"
        f" Cliente]: {row['review_comment_message']}"
    )

  df_enriquecido["document_text"] = df_enriquecido.apply(
      construir_documento_texto, axis=1
  )

  df_final = df_enriquecido[[
      "review_id",
      "order_id",
      "review_score",
      "order_purchase_timestamp",
      "review_comment_message",
      "document_text",
  ]]

  # Garantir que a pasta processed existe e exportar o ficheiro CSV
  os.makedirs(caminho_processed, exist_ok=True)
  caminho_arquivo_saida = os.path.join(caminho_processed, "reviews_clean.csv")
  df_final.to_csv(caminho_arquivo_saida, index=False, encoding="utf-8")

  print(f"Ficheiro guardado com sucesso em: {caminho_arquivo_saida}")
  return df_final


if __name__ == "__main__":
  carregar_e_limpar_dados()