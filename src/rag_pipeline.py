import os
import chromadb
from sentence_transformers import SentenceTransformer


class RAGVoiceOfCustomer:

  def __init__(self):
    raiz_projeto = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    self.caminho_chroma = os.path.join(raiz_projeto, "data", "chroma_db")

    print("A inicializar o motor de RAG e a carregar modelos locais...")
    # 1. Carregar o mesmo modelo de embeddings usado na indexação
    self.modelo_embeddings = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # 2. Conectar ao ChromaDB local
    self.cliente_chroma = chromadb.PersistentClient(path=self.caminho_chroma)
    self.colecao = self.cliente_chroma.get_collection(name="olist_reviews_voc")

  def recuperar_evidencias(self, pergunta: str, k: int = 5):
    """Realiza a busca semântica na base vetorial para recuperar as avaliações

    mais relevantes para a pergunta do utilizador.
    """
    # Transformar a pergunta do utilizador em vetor
    vetor_pergunta = self.modelo_embeddings.encode([pergunta]).tolist()

    # Buscar no ChromaDB os k documentos mais próximos semanticamente
    resultados = self.colecao.query(
        query_embeddings=vetor_pergunta, n_results=k
    )

    documentos = resultados["documents"][0]
    metadados = resultados["metadatas"][0]

    return documentos, metadados

  def construir_prompt_e_contexto(self, pergunta: str, documentos: list):
    """Constrói o contexto estruturado fundamentado em evidências reais

    e define as regras para evitar alucinações e respostas sem suporte nos dados.
    """
    if not documentos:
      return (
          "Não foram encontradas avaliações relevantes na base de dados para"
          " responder a esta pergunta."
      )

    # Unir os documentos recuperados num bloco de contexto limpo
    contexto_unificado = "\n\n---\n\n".join(documentos)

    # Prompt estruturado com diretrizes rígidas anti-alucinação (Requisito 4 do edital)
    prompt = f"""
        És um assistente especializado em Voice of Customer Intelligence para uma empresa de e-commerce.
        O teu objetivo é analisar as avaliações reais dos clientes da Olist e responder à pergunta do gestor.

        DIRETRIZES DE SEGURANÇA E RIGOR:
        1. Baseia a tua resposta EXCLUSIVAMENTE nas evidências fornecidas abaixo.
        2. Se as evidências recuperadas forem insuficientes ou não contiverem a resposta para a pergunta, deves reconhecer explicitamente as tuas limitações e responder: "Não possuo avaliações suficientes na base de dados para responder a esta pergunta com segurança."
        3. Nunca inventes informações ou alucines dados que não estejam presentes nos comentários dos clientes.
        4. Sempre que possível, cita trechos ou dados das avaliações recuperadas para fundamentar os teus insights.

        ---
        EVIDÊNCIAS REAIS DOS CLIENTES (CONTEXTO):
        {contexto_unificado}
        ---

        PERGUNTAS DO GESTOR:
        {pergunta}

        RESPOSTA FUNDAMENTADA:
        """
    return prompt

  def responder(self, pergunta: str):
    print(f"\n a processar a pergunta: '{pergunta}'")

    # Passo A: Recuperar as avaliações mais relevantes
    docs, metas = self.recuperar_evidencias(pergunta, k=5)

    # Passo B: Construir o contexto
    prompt_final = self.construir_prompt_e_contexto(pergunta, docs)

    print("\n--- PROMPT GERADO PARA O LLM ---")
    print(prompt_final[:800] + "...\n[Conteúdo truncado para visualização]")
    print("---------------------------------")

    # Nota: Aqui podes enviar o 'prompt_final' para o teu LLM gratuito (via Ollama local ou API)
    return prompt_final, docs


if __name__ == "__main__":
  rag = RAGVoiceOfCustomer()

  # Teste prático de pergunta baseada nos requisitos do Tech Challenge
  pergunta_teste = (
      "Quais são os principais problemas relatados pelos clientes"
      " relacionados com atrasos na entrega?"
  )
  prompt, evidencias = rag.responder(pergunta_teste)