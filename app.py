import os
import csv
import unicodedata
from collections import Counter
from datetime import datetime
import streamlit as st
import plotly.express as px

from src.prompt_config import SYSTEM_PROMPT, detetar_intencao

st.set_page_config(
    page_title="Tech Challenge - Fase 4 | FIAP Pos-Tech",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700&family=Rajdhani:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #050406;
        background-image:
            radial-gradient(circle, rgba(238, 0, 111, 0.22) 1px, transparent 1.4px),
            radial-gradient(circle, rgba(255, 255, 255, 0.13) 0.8px, transparent 1.3px),
            radial-gradient(ellipse at 50% 0%, rgba(100, 0, 52, 0.2), transparent 55%);
        background-size: 19px 19px, 31px 31px, auto;
        background-position: 0 0, 8px 12px, center top;
        color: #eee8ed;
        font-family: 'Rajdhani', 'Bahnschrift', 'Arial Narrow', sans-serif;
        min-height: 100vh;
    }
    html, body { background-color: #050406 !important; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
    }
    [data-testid="stBottomBlockContainer"] > div {
        background-color: #050406 !important;
        background-image:
            radial-gradient(circle, rgba(238, 0, 111, 0.22) 1px, transparent 1.4px),
            radial-gradient(circle, rgba(255, 255, 255, 0.13) 0.8px, transparent 1.3px);
        background-size: 19px 19px, 31px 31px;
        background-position: 0 0, 8px 12px;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: rgba(8, 6, 10, 0.96);
        border-right: 1px solid rgba(255, 0, 117, 0.35);
    }
    [data-testid="stChatInput"] {
        background: rgba(12, 8, 13, 0.96) !important;
        border: 1px solid rgba(255, 0, 117, 0.42);
        border-radius: 3px;
    }
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        box-shadow: none !important;
    }
    h1, h2, h3 {
        color: #fff !important;
        font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif;
        letter-spacing: 0;
    }
    .brand-lockup {
        position: relative;
        isolation: isolate;
        max-width: 48rem;
        margin: 0 auto 1.4rem;
        padding: 1.7rem 1rem 1.1rem;
        text-align: center;
    }
    .brand-lockup::before, .brand-lockup::after {
        position: absolute;
        top: 0;
        left: 50%;
        z-index: -1;
        content: '';
        transform: translateX(-50%);
        clip-path: polygon(20% 0, 80% 0, 100% 50%, 80% 100%, 20% 100%, 0 50%);
        border: 1px solid rgba(255, 0, 117, 0.34);
        pointer-events: none;
    }
    .brand-lockup::before { width: min(76vw, 34rem); height: 12.5rem; }
    .brand-lockup::after {
        top: 1.4rem;
        width: min(48vw, 20rem);
        height: 9.5rem;
        border-color: rgba(255, 0, 117, 0.22);
    }
    .brand-mark {
        color: #f00075;
        font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif;
        font-size: 5rem;
        font-weight: 500;
        line-height: 1;
        text-shadow: 0 0 22px rgba(240, 0, 117, 0.35);
    }
    .brand-kicker {
        margin: 0.7rem 0 0.2rem;
        color: #f5edf2;
        font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif;
        font-size: 0.85rem;
    }
    .brand-subtitle {
        margin: 0;
        color: #c7bac3;
        font-size: 1.2rem;
        font-weight: 500;
    }
    .stChatMessage {
        background: rgba(14, 10, 15, 0.92) !important;
        border: 1px solid rgba(255, 0, 117, 0.25);
        border-radius: 3px;
        color: #f1eaf0;
    }
    .stButton > button {
        background: #ed006f !important;
        color: #fff !important;
        border: 1px solid #ff3b98 !important;
        border-radius: 2px;
        font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: #ff1687 !important;
        border-color: #ff75b7 !important;
    }
    .streamlit-expanderHeader {
        background: rgba(13, 9, 14, 0.94) !important;
        color: #ff4b9c !important;
        border: 1px solid rgba(255, 0, 117, 0.32);
        border-radius: 2px;
    }
    [data-testid="stSidebar"] h3 { font-size: 0.95rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { font-size: 1rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label { font-size: 0.75rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        border-left: 2px solid rgba(240, 0, 117, 0.65);
        padding: 0.25rem 0.6rem;
        background: rgba(18, 11, 18, 0.7);
    }
    [data-testid="stChatInput"] textarea {
        background: rgba(12, 8, 13, 0.96);
        color: #f5edf2;
        border-color: rgba(255, 0, 117, 0.42);
        font-family: 'Rajdhani', 'Bahnschrift', 'Arial Narrow', sans-serif;
    }
    @media (max-width: 640px) {
        .brand-lockup { padding-top: 1.4rem; }
        .brand-lockup::before { height: 10rem; }
        .brand-lockup::after { height: 7.5rem; }
        .brand-mark { font-size: 3.6rem; }
        .brand-kicker { font-size: 0.72rem; }
        .brand-subtitle { font-size: 1rem; }
    }
    @media (max-width: 800px) {
        .brand-mark { font-size: 3.2rem; }
        .brand-subtitle { font-size: 0.95rem; }
        .brand-lockup::before { width: 90%; }
        .brand-lockup::after { width: 62%; }
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def carregar_motor_rag():
    raiz_projeto = os.path.dirname(__file__)
    caminho_chroma = os.path.join(raiz_projeto, "data", "chroma_db")
    modelo = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    cliente = chromadb.PersistentClient(path=caminho_chroma)
    colecao = cliente.get_collection(name="olist_reviews_voc")
    return modelo, colecao

with st.spinner("A carregar base vetorial e motor RAG..."):
    modelo_embeddings, colecao = carregar_motor_rag()

st.markdown("""
    <div class="brand-lockup">
        <div class="brand-mark">FIAP</div>
        <p class="brand-kicker">POS TECH · FASE 4</p>
        <p class="brand-subtitle">Voice of Customer Intelligence · Olist</p>
    </div>
""", unsafe_allow_html=True)

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "pergunta_pendente" not in st.session_state:
    st.session_state.pergunta_pendente = None
if "cat_selecionada" not in st.session_state:
    st.session_state.cat_selecionada = None

@st.cache_data
def obter_ranking_global_absoluto():
    resultados_globais = colecao.get(include=["metadatas"])
    metadatas_todas = resultados_globais["metadatas"]

    negativas, positivas, todas = [], [], []
    for meta in metadatas_todas:
        try:
            score = int(float(meta.get("review_score", 3)))
        except (ValueError, TypeError):
            score = 3
        cat = meta.get("product_category_name", "desconhecido")

        todas.append(cat)
        if score <= 2:
            negativas.append(cat)
        elif score >= 4:
            positivas.append(cat)

    return Counter(negativas), Counter(positivas), Counter(todas)

ranking_negativo_global, ranking_positivo_global, ranking_geral_global = obter_ranking_global_absoluto()

@st.cache_data
def obter_resumo_base():
    resultados = colecao.get(include=["metadatas"])
    metadatas_todas = resultados["metadatas"]

    total_avaliacoes = len(metadatas_todas)
    positivas = 0
    negativas = 0
    categorias = Counter()

    for meta in metadatas_todas:
        try:
            score = int(float(meta.get("review_score", 3)))
        except (ValueError, TypeError):
            score = 3

        categoria = meta.get("product_category_name", "desconhecido")
        categorias[categoria] += 1

        if score <= 2:
            negativas += 1
        elif score >= 4:
            positivas += 1

    categoria_mais_frequente = categorias.most_common(1)[0] if categorias else ("desconhecido", 0)
    categoria_nome = categoria_mais_frequente[0].replace("_", " ").title()

    return {
        "total": total_avaliacoes,
        "positivas": positivas,
        "negativas": negativas,
        "categoria_top": categoria_nome,
        "categoria_top_total": categoria_mais_frequente[1],
    }

@st.cache_data
def obter_kpis_por_categoria():
    categoria_mais_reclamada = ranking_negativo_global.most_common(1)[0] if ranking_negativo_global else ("desconhecido", 0)
    categoria_mais_positiva = ranking_positivo_global.most_common(1)[0] if ranking_positivo_global else ("desconhecido", 0)
    categoria_mais_frequente = ranking_geral_global.most_common(1)[0] if ranking_geral_global else ("desconhecido", 0)

    return {
        "critica": {
            "nome": categoria_mais_reclamada[0].replace("_", " ").title(),
            "valor": categoria_mais_reclamada[1],
        },
        "melhor": {
            "nome": categoria_mais_positiva[0].replace("_", " ").title(),
            "valor": categoria_mais_positiva[1],
        },
        "mais_vista": {
            "nome": categoria_mais_frequente[0].replace("_", " ").title(),
            "valor": categoria_mais_frequente[1],
        },
    }

def limpar_texto(txt):
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return txt.replace(" e ", " ").replace(",", " ").lower()

with st.sidebar:
    st.markdown("<h2 style='color: #ff0055; margin-bottom: 0;'>POS TECH</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; font-size: 0.85rem;'>FIAP - IA & Machine Learning</p>", unsafe_allow_html=True)
    st.markdown("---")

    resumo_base = obter_resumo_base()
    st.markdown("### Resumo da Base")
    st.metric("Avaliações", resumo_base["total"])
    st.metric("Elogios", resumo_base["positivas"])
    st.metric("Reclamações", resumo_base["negativas"])
    st.caption(f"Categoria mais frequente: {resumo_base['categoria_top']} ({resumo_base['categoria_top_total']} registros)")

    st.markdown("---")
    st.markdown("### KPIs por Categoria")
    categorias_kpi = ["Todas as categorias", *sorted(ranking_geral_global)]
    categoria_kpi = st.selectbox(
        "Categoria",
        categorias_kpi,
        key="categoria_kpi",
        format_func=lambda categoria: (
            categoria if categoria == "Todas as categorias"
            else categoria.replace("_", " ").title()
        ),
    )
    if categoria_kpi == "Todas as categorias":
        total_categoria = sum(ranking_geral_global.values())
        positivas_categoria = sum(ranking_positivo_global.values())
        negativas_categoria = sum(ranking_negativo_global.values())
    else:
        total_categoria = ranking_geral_global[categoria_kpi]
        positivas_categoria = ranking_positivo_global[categoria_kpi]
        negativas_categoria = ranking_negativo_global[categoria_kpi]

    st.metric("Avaliações", total_categoria)
    st.metric("Elogios (notas 4-5)", positivas_categoria)
    st.metric("Reclamações (notas 1-2)", negativas_categoria)

    st.markdown("---")
    if st.button("Limpar Conversa"):
        st.session_state.mensagens = []
        st.session_state.pergunta_pendente = None
        st.session_state.cat_selecionada = None
        st.rerun()

# --- RENDERIZAR HISTÓRICO ---
for idx, mensagem in enumerate(st.session_state.mensagens):
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["conteudo_texto"], unsafe_allow_html=True)
        if mensagem.get("figura_grafico"):
            st.plotly_chart(mensagem["figura_grafico"], use_container_width=True)
            
        if "evidencias" in mensagem and mensagem["evidencias"]:
            limite_atual = mensagem.get("limite_atual", 5)
            evidencias_visiveis = mensagem["evidencias"][:limite_atual]
            
            with st.expander(f"🔍 Ver Evidências Reais Auditáveis (Exibindo {len(evidencias_visiveis)} de {len(mensagem['evidencias'])})"):
                for doc, meta in evidencias_visiveis:
                    st.markdown(
                        f"**Categoria:** `{meta.get('product_category_name')}` | "
                        f"**Nota:** `{meta.get('review_score')}/5` | **Data:** `{meta.get('order_purchase_timestamp')}`"
                    )
                    st.text(doc)
                    st.divider()
                
                if len(evidencias_visiveis) < len(mensagem["evidencias"]):
                    if st.button("Carregar mais 5 evidências", key=f"btn_carregar_hist_{idx}"):
                        mensagem["limite_atual"] += 5
                        st.rerun()

        if mensagem.get("exigir_ranking_flag") and mensagem.get("resto_ranking"):
            modo_porcentagem = mensagem.get("modo_porcentagem", False)
            total_ctx = mensagem.get("total_contexto", 1)
            with st.expander("📈 Ver restante do Ranking Completo de Categorias"):
                for pos, (cat, freq) in enumerate(mensagem["resto_ranking"], 6):
                    if modo_porcentagem:
                        perc = (freq / total_ctx) * 100 if total_ctx > 0 else 0
                        st.markdown(f"{pos}. `{cat}` — **{perc:.1f}%** ({freq} ocorrência(s))")
                    else:
                        st.markdown(f"{pos}. `{cat}` — **{freq} ocorrência(s)**")

        if mensagem.get("mostrar_botoes_categorias"):
            cols = st.columns(5)
            top_cats = [c for c, _ in ranking_negativo_global.most_common(5)]
            for i, cat in enumerate(top_cats):
                with cols[i]:
                    if st.button(cat.replace("_", " "), key=f"btn_cat_hist_{idx}_{cat}"):
                        st.session_state.cat_selecionada = cat
                        st.session_state.pergunta_pendente = "problemas"
                        st.rerun()

def processar_resposta(pergunta_utilizador, categoria_forçada=None):
    with st.chat_message("assistant"):
        with st.spinner("A analisar dados e a estruturar resposta rigorosa..."):
            vetor_pergunta = modelo_embeddings.encode([pergunta_utilizador]).tolist()
            intencao = detetar_intencao(pergunta_utilizador)

            pergunta_lower = pergunta_utilizador.lower()
            pergunta_limpa = limpar_texto(pergunta_utilizador)
            
            pediu_grafico = any(termo in pergunta_lower for termo in ["grafico", "gráfico", "pizza", "barra", "plot"])
            pergunta_porcentagem = "porcentagem" in pergunta_lower or "por cento" in pergunta_lower or "%" in pergunta_lower
            
            termos_comparacao = ["mais pessoas reclamando", "mais reclamando ou elogiando", "reclama ou elogia", "comparar", "positivas ou negativas", "negativas ou positivas", "elogios ou reclamações", "reclamações ou elogios"]
            pede_comparacao = any(termo in pergunta_lower for termo in termos_comparacao)
            
            categoria_alvo = categoria_forçada
            if not categoria_alvo:
                for cat_possivel in ranking_geral_global.keys():
                    cat_mapeada = cat_possivel.replace("_", " ")
                    if cat_mapeada in pergunta_limpa or cat_possivel in pergunta_limpa:
                        categoria_alvo = cat_possivel
                        break

            if categoria_alvo:
                pede_categorias_problema = False
                pede_analise_problemas = False
            else:
                pede_categorias_problema = any(termo in pergunta_lower for termo in ["categoria", "categorias", "ranking", "principais"]) and not pede_comparacao
                pede_analise_problemas = any(termo in pergunta_lower for termo in ["problema", "problemas", "motivo", "motivos", "defeito", "atraso", "logistica"]) and not pede_categorias_problema and not pede_comparacao

            if intencao == "negativa":
                ranking_ativo = ranking_negativo_global
                total_contexto = sum(ranking_negativo_global.values())
            elif intencao == "positiva" or "elogiados" in pergunta_lower:
                ranking_ativo = ranking_positivo_global
                total_contexto = sum(ranking_positivo_global.values())
            else:
                ranking_ativo = ranking_geral_global
                total_contexto = sum(ranking_geral_global.values())

            figura_plotly = None
            deve_mostrar_ranking = False
            mostrar_botoes_categorias = False
            resto_ranking = []
            top_5 = []

            if pede_comparacao and categoria_alvo:
                neg_cat = ranking_negativo_global.get(categoria_alvo, 0)
                pos_cat = ranking_positivo_global.get(categoria_alvo, 0)
                
                resposta_texto = (
                    f"### 📊 Análise Comparativa para a Categoria: `{categoria_alvo}`\n\n"
                    f"- **Reclamações (Notas 1 e 2):** `{neg_cat}` ocorrência(s)\n"
                    f"- **Elogios (Notas 4 e 5):** `{pos_cat}` ocorrência(s)\n\n"
                )
                if neg_cat > pos_cat:
                    resposta_texto += f"👉 Nesta categoria, existem **mais pessoas a reclamar** do que a elogiar."
                elif pos_cat > neg_cat:
                    resposta_texto += f"👉 Nesta categoria, existem **mais pessoas a elogiar** do que a reclamar."
                else:
                    resposta_texto += f"👉 Há um equilíbrio exato entre reclamações e elogios nesta categoria."
            elif pede_analise_problemas and not categoria_alvo:
                st.session_state.pergunta_pendente = pergunta_utilizador
                resposta_texto = (
                    "### ⚠️ Análise Geral dos Principais Problemas:\n\n"
                    "Num panorama macro da operação, os clientes demonstram insatisfação principalmente por 3 motivos centrais:\n"
                    "1. **Logística:** Atrasos nas entregas e falhas nas transportadoras.\n"
                    "2. **Qualidade:** Produtos que chegam com defeito ou não correspondem ao anúncio.\n"
                    "3. **Pós-Venda:** Dificuldade no contacto e estorno com os parceiros.\n\n"
                    "**Para analisar as evidências detalhadas de um setor, selecione uma das categorias mais afetadas abaixo:**"
                )
                mostrar_botoes_categorias = True
            else:
                deve_mostrar_ranking = bool(pede_categorias_problema or pediu_grafico or pergunta_porcentagem or "elogiados" in pergunta_lower) and not categoria_alvo
                top_5 = ranking_ativo.most_common(5)
                resto_ranking = ranking_ativo.most_common()[5:]

                if categoria_alvo:
                    if intencao == "positiva" or "elogi" in pergunta_lower or "positiv" in pergunta_lower:
                        resposta_texto = (
                            f"### 🔍 Análise de Elogios da Categoria: `{categoria_alvo}`\n\n"
                            f"Com base na auditoria das avaliações reais, os clientes desta categoria destacam a excelente qualidade, "
                            f"o ótimo custo-benefício e a rapidez na entrega. Consulte as evidências de satisfação abaixo."
                        )
                    elif intencao == "negativa" or "reclam" in pergunta_lower or "negativ" in pergunta_lower or "problema" in pergunta_lower:
                        resposta_texto = (
                            f"### 🔍 Análise de Problemas da Categoria: `{categoria_alvo}`\n\n"
                            f"Com base na auditoria das avaliações de insatisfação (notas 1 e 2), os clientes desta categoria reportam "
                            f"falhas logísticas, atrasos e divergências ou avarias no produto. Consulte os relatos na íntegra abaixo."
                        )
                    else:
                        # Resumo neutro/misto cruza os dois cenários
                        neg_cat = ranking_negativo_global.get(categoria_alvo, 0)
                        pos_cat = ranking_positivo_global.get(categoria_alvo, 0)
                        resposta_texto = (
                            f"### 🔍 Resumo Geral da Categoria: `{categoria_alvo}`\n\n"
                            f"Esta categoria apresenta um cenário misto de interações:\n"
                            f"- **Lado Positivo ({pos_cat} elogios):** Os consumidores elogiam a utilidade e a entrega dos produtos corretos.\n"
                            f"- **Lado Negativo ({neg_cat} reclamações):** As principais queixas envolvem logística demorada ou itens trocados.\n\n"
                            f"Consulte as evidências auditáveis abaixo com diferentes níveis de satisfação."
                        )
                elif deve_mostrar_ranking:
                    ranking_texto = "### 🏆 Ranking de Categorias:\n"
                    for pos, (cat, freq) in enumerate(top_5, 1):
                        ranking_texto += f"{pos}. `{cat}` — **{freq} ocorrência(s)**\n"

                    if pergunta_porcentagem or pediu_grafico:
                        resposta_porcentagem = "### 📊 Porcentagem por Categoria:\n\n"
                        dados_grafico = []
                        soma_top_5 = 0
                        for cat, freq in top_5:
                            porcentagem = (freq / total_contexto) * 100 if total_contexto > 0 else 0
                            resposta_porcentagem += f"- **{cat}**: `{porcentagem:.1f}%` ({freq} ocorrência(s))\n"
                            dados_grafico.append({"Categoria": cat, "Ocorrências": freq})
                            soma_top_5 += freq
                        
                        # Adicionar "Outras Categorias" para que a percentagem da pizza não distorça
                        outros = total_contexto - soma_top_5
                        if outros > 0:
                            dados_grafico.append({"Categoria": "Outras Categorias", "Ocorrências": outros})
                        
                        resposta_texto = resposta_porcentagem

                        if pediu_grafico:
                            import pandas as pd
                            df_pizza = pd.DataFrame(dados_grafico)
                            figura_plotly = px.pie(
                                df_pizza, 
                                names="Categoria", 
                                values="Ocorrências", 
                                title="Distribuição Percentual Absoluta (Base Global)",
                                color_discrete_sequence=px.colors.sequential.RdBu
                            )
                            figura_plotly.update_layout(
                                paper_bgcolor="#0c0c0c",
                                plot_bgcolor="#0c0c0c",
                                font_color="#e0e0e0"
                            )
                    elif intencao == "positiva" or "elogiados" in pergunta_lower:
                        resposta_texto = (
                            "**Análise de Elogios e Satisfação:**\n"
                            "Abaixo encontram-se as 5 categorias com maior volume absoluto de avaliações positivas (notas 4 e 5):\n\n"
                            f"{ranking_texto}"
                        )
                    else:
                        resposta_texto = (
                            "**Panorama Geral das Categorias com Mais Problemas:**\n"
                            "Abaixo encontram-se as 5 categorias com maior volume absoluto de reclamações reportadas:\n\n"
                            f"{ranking_texto}"
                        )
                else:
                    resposta_texto = (
                        "**Análise de Voz do Cliente:**\n"
                        "Com base nos registos recuperados da base da Olist, consulte as evidências auditáveis abaixo."
                    )

            resultados_busca = colecao.query(query_embeddings=vetor_pergunta, n_results=60)
            documentos_raw = resultados_busca["documents"][0]
            metadados_raw = resultados_busca["metadatas"][0]

            documentos_validos = []
            metadados_validos = []

            for doc, meta in zip(documentos_raw, metadados_raw):
                try:
                    score = int(float(meta.get("review_score", 3)))
                except (ValueError, TypeError):
                    score = 3
                cat = meta.get("product_category_name", "desconhecido")

                if categoria_alvo and cat != categoria_alvo:
                    continue

                if intencao == "negativa" and score <= 2:
                    documentos_validos.append(doc)
                    metadados_validos.append(meta)
                elif (intencao == "positiva" or "elogiados" in pergunta_lower) and score >= 4:
                    documentos_validos.append(doc)
                    metadados_validos.append(meta)
                elif intencao == "neutra" and not pede_comparacao:
                    documentos_validos.append(doc)
                    metadados_validos.append(meta)

            if categoria_alvo and len(documentos_validos) == 0:
                for doc, meta in zip(documentos_raw, metadados_raw):
                    if meta.get("product_category_name") == categoria_alvo:
                        documentos_validos.append(doc)
                        metadados_validos.append(meta)

            st.markdown(resposta_texto, unsafe_allow_html=True)
            if figura_plotly:
                st.plotly_chart(figura_plotly, use_container_width=True)

            par_evidencias = list(zip(documentos_validos, metadados_validos))
            limite_inicial = 5

            msg_nova = {
                "role": "assistant",
                "conteudo_texto": resposta_texto,
                "figura_grafico": figura_plotly,
                "evidencias": par_evidencias,
                "limite_atual": limite_inicial,
                "exigir_ranking_flag": deve_mostrar_ranking,
                "resto_ranking": resto_ranking,
                "modo_porcentagem": pergunta_porcentagem,
                "total_contexto": total_contexto,
                "mostrar_botoes_categorias": mostrar_botoes_categorias
            }
            st.session_state.mensagens.append(msg_nova)

            if deve_mostrar_ranking and resto_ranking:
                with st.expander("📈 Ver restante do Ranking Completo de Categorias"):
                    for pos, (cat, freq) in enumerate(resto_ranking, 6):
                        if pergunta_porcentagem:
                            perc = (freq / total_contexto) * 100 if total_contexto > 0 else 0
                            st.markdown(f"{pos}. `{cat}` — **{perc:.1f}%** ({freq} ocorrência(s))")
                        else:
                            st.markdown(f"{pos}. `{cat}` — **{freq} ocorrência(s)**")

            if mostrar_botoes_categorias:
                cols = st.columns(5)
                top_cats = [c for c, _ in ranking_negativo_global.most_common(5)]
                for i, cat in enumerate(top_cats):
                    with cols[i]:
                        if st.button(cat.replace("_", " "), key=f"btn_novo_cat_{cat}_{len(st.session_state.mensagens)}"):
                            st.session_state.cat_selecionada = cat
                            st.session_state.pergunta_pendente = pergunta_utilizador
                            st.rerun()

            evidencias_visiveis = par_evidencias[:limite_inicial]
            if par_evidencias:
                with st.expander(f"🔍 Ver Evidências Reais Auditáveis (Exibindo {len(evidencias_visiveis)} de {len(par_evidencias)})"):
                    for i, (doc, meta) in enumerate(evidencias_visiveis):
                        st.markdown(
                            f"**Evidência {i+1}** | **Categoria:** `{meta.get('product_category_name')}` | "
                            f"**Nota:** `{meta.get('review_score')}/5` | **Data:** `{meta.get('order_purchase_timestamp')}`"
                        )
                        st.text(doc)
                        st.divider()

                    if len(evidencias_visiveis) < len(par_evidencias):
                        if st.button("Carregar mais 5 evidências", key=f"btn_novo_carregar_{len(st.session_state.mensagens)}"):
                            st.session_state.mensagens[-1]["limite_atual"] += 5
                            st.rerun()

if st.session_state.cat_selecionada:
    cat_escolhida = st.session_state.cat_selecionada
    st.session_state.cat_selecionada = None
    pergunta_anterior = st.session_state.get("pergunta_pendente", "problemas")
    st.session_state.mensagens.append({"role": "user", "conteudo_texto": f"Quero ver os problemas da categoria: {cat_escolhida}"})
    with st.chat_message("user"):
        st.markdown(f"Quero ver os problemas da categoria: `{cat_escolhida}`")
    processar_resposta(pergunta_anterior, categoria_forçada=cat_escolhida)

if pergunta_utilizador := st.chat_input("Digite sua pergunta sobre as avaliacoes da Olist..."):
    st.session_state.mensagens.append({"role": "user", "conteudo_texto": pergunta_utilizador})
    with st.chat_message("user"):
        st.markdown(pergunta_utilizador)

    processar_resposta(pergunta_utilizador)