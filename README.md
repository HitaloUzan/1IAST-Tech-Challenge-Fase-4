# 1IAST-Tech-Challenge-Fase-4
Solução de Voice of Customer Intelligence baseada em RAG para exploração inteligente de avaliações de e-commerce da Olist.

tech-challenge-fase4/
│
├── data/
│   ├── raw/                 # CSVs originais baixados do Kaggle (orders, products, reviews)
│   └── processed/           # CSV final limpo e pronto para indexação
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py     # Script do Passo 2 (Limpeza e cruzamento de dados)
│   ├── embeddings.py        # Script do Passo 3 (Geração de embeddings e banco vetorial)
│   └── rag_pipeline.py      # Script dos Passos 4 e 5 (Recuperação e LLM)
│
├── app.py                   # Interface de chat/investigação (ex: Streamlit)
├── requirements.txt         # Dependências do projeto
└── README.md