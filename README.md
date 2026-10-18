# ⚡ Tech Challenge - Fase 4 | FIAP Pós-Tech
### Voice of Customer (VoC) Intelligence - Olist E-commerce

Projeto desenvolvido para a Fase 4 da Pós-Graduação em Inteligência Artificial & Machine Learning da **FIAP**.

---

## 📌 Visão Geral do Projeto

Este projeto implementa um assistente inteligente baseado em **RAG (Retrieval-Augmented Generation)** focado na análise de *Voice of Customer* (VoC), utilizando o dataset público de avaliações do e-commerce brasileiro **Olist**.

O objetivo principal é extrair insights qualitativos e quantitativos a partir dos comentários dos clientes, permitindo aos gestores entenderem rapidamente os principais gargalos operacionais — como logística, defeitos e atendimento — e os pontos fortes dos produtos, de forma auditável e transparente.

## 🏗️ Arquitetura e Tecnologias Utilizadas

A aplicação foi construída com foco em performance, processamento local de NLP e interatividade.

- **Interface Web:** [Streamlit](https://streamlit.io/) — interface reativa e gestão de estado.
- **Banco de dados vetorial:** [ChromaDB](https://www.trychroma.com/) — armazenamento local persistente dos embeddings das avaliações.
- **Modelos de embedding:** [Sentence-Transformers](https://sbert.net/) (`paraphrase-multilingual-MiniLM-L12-v2`, via Hugging Face) — vetorização semântica multilíngue, com suporte a português brasileiro.
- **Visualização de dados:** [Plotly Express](https://plotly.com/python/plotly-express/) — geração de gráficos interativos.
- **Linguagem:** Python 3.10+.

## ✨ Principais Funcionalidades

1. **Análise macro e quantitativa:** gera rankings e proporções percentuais das categorias com maior volume de reclamações ou elogios.
2. **Análise qualitativa e semântica:** identifica causas recorrentes dos problemas — como atrasos na entrega e produtos avariados — sem exigir que o usuário informe uma categoria específica, com apoio de botões interativos dinâmicos.
3. **Análise comparativa:** compara o volume de avaliações positivas e negativas dentro de uma mesma categoria.
4. **Auditoria e transparência:** apresenta as respostas com uma área de **Evidências Reais**, permitindo consultar a nota, a data e o texto original da avaliação que fundamentou a resposta, com paginação.
5. **Interatividade inteligente:** roteia dinamicamente as intenções e adapta a resposta conforme a pergunta, como resumo geral, comparação ou foco em um sentimento específico.

## 📂 Estrutura do Repositório

```text
1IAST-Tech-Challenge-Fase-4/
├── data/
│   ├── chroma_db/            # Banco vetorial populado com embeddings
│   ├── processed/            # Dados limpos e processados
│   └── raw/                  # Dados brutos originais da Olist
├── src/
│   ├── __init__.py
│   ├── embeddings.py         # Geração de embeddings
│   ├── preprocessing.py      # Limpeza e preparação dos dados
│   ├── prompt_config.py      # Prompts e detecção de intenção (NLP)
│   └── rag_pipeline.py       # Orquestração do RAG e ingestão na base vetorial
├── app.py                    # Aplicação Streamlit e lógica do RAG
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação
```

## 🚀 Como Executar o Projeto Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/1IAST-Tech-Challenge-Fase-4.git
cd 1IAST-Tech-Challenge-Fase-4
```

> **Observação:** substitua `SEU-USUARIO` pelo nome de usuário ou organização responsável pelo repositório no GitHub.

### 2. Crie e ative um ambiente virtual

Crie o ambiente virtual:

```bash
python -m venv venv
```

Ative-o conforme o sistema operacional.

**Windows (Prompt de Comando):**

```bat
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Instale as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação Streamlit

```bash
streamlit run app.py
```

A aplicação deverá abrir no navegador padrão. Caso isso não aconteça, acesse [http://localhost:8501](http://localhost:8501).

## 🧪 Roteiro de Testes Recomendado

Para explorar os recursos do orquestrador de RAG, experimente as perguntas abaixo na interface.

### 1. Análise macro

**Pergunta:**

> Quais são as principais reclamações dos clientes?

**Objetivo:** identificar os principais temas de reclamação presentes nos dados.

### 2. Geração de gráficos

**Pergunta:**

> Qual a porcentagem de clientes insatisfeitos por categoria?

**Objetivo:** explorar a análise percentual e a visualização dos resultados por categoria.

### 3. Interatividade com botões

**Pergunta:**

> Quais são os problemas enfrentados pelos clientes?

**Objetivo:** visualizar os problemas identificados e interagir com os botões de categoria apresentados pela aplicação.

### 4. Análise direta e específica

**Pergunta:**

> Sobre qual motivo a categoria cama_mesa_banho teve mais reclamações?

**Objetivo:** investigar os motivos de reclamação de uma categoria específica.

### 5. Análise comparativa

**Pergunta:**

> Sobre a categoria informática e acessórios, tem mais pessoas reclamando ou elogiando?

**Objetivo:** comparar manifestações positivas e negativas relacionadas à categoria.

### 6. Foco positivo

**Pergunta:**

> Quais são os produtos mais elogiados pelos clientes?

**Objetivo:** identificar produtos que se destacam pelas avaliações positivas.

## 📋 Requisitos e Observações

- Python 3.10 ou superior.
- Arquivo `requirements.txt` na raiz do projeto.
- Arquivo `app.py` na raiz do projeto.
- Os diretórios e arquivos de dados necessários devem estar disponíveis conforme a configuração do projeto.

> **Nota:** se a aplicação depender de variáveis de ambiente, chaves de API ou arquivos de configuração adicionais, configure-os antes de executar o Streamlit.
