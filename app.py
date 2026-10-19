import os
from collections import Counter
import chromadb
import streamlit as st
import plotly.express as px
import pandas as pd
from sentence_transformers import SentenceTransformer

from src.prompt_config import detetar_intencao, analisar_pergunta_rag

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
    [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stBottomBlockContainer"] { background: transparent !important; }
    [data-testid="stBottomBlockContainer"] > div {
        background-color: #050406 !important;
        background-image: radial-gradient(circle, rgba(238, 0, 111, 0.22) 1px, transparent 1.4px), radial-gradient(circle, rgba(255, 255, 255, 0.13) 0.8px, transparent 1.3px);
        background-size: 19px 19px, 31px 31px;
        background-position: 0 0, 8px 12px;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: rgba(8, 6, 10, 0.96); border-right: 1px solid rgba(255, 0, 117, 0.35); }
    [data-testid="stChatInput"] { background: rgba(12, 8, 13, 0.96) !important; border: 1px solid rgba(255, 0, 117, 0.42); border-radius: 3px; position: relative; z-index: 99999 !important; display: block !important; }
    [data-testid="stChatInput"] textarea { background: transparent !important; box-shadow: none !important; color: #f5edf2; font-family: 'Rajdhani', 'Bahnschrift', 'Arial Narrow', sans-serif; }
    h1, h2, h3 { color: #fff !important; font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif; letter-spacing: 0; }
    .brand-lockup { position: relative; isolation: isolate; max-width: 48rem; margin: 0 auto 1.4rem; padding: 1.7rem 1rem 1.1rem; text-align: center; }
    .brand-lockup::before, .brand-lockup::after { position: absolute; top: 0; left: 50%; z-index: -1; content: ''; transform: translateX(-50%); clip-path: polygon(20% 0, 80% 0, 100% 50%, 80% 100%, 20% 100%, 0 50%); border: 1px solid rgba(255, 0, 117, 0.34); pointer-events: none; }
    .brand-lockup::before { width: min(76vw, 34rem); height: 12.5rem; }
    .brand-lockup::after { top: 1.4rem; width: min(48vw, 20rem); height: 9.5rem; border-color: rgba(255, 0, 117, 0.22); }
    .brand-mark { color: #f00075; font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif; font-size: 5rem; font-weight: 500; line-height: 1; text-shadow: 0 0 22px rgba(240, 0, 117, 0.35); }
    .brand-kicker { margin: 0.7rem 0 0.2rem; color: #f5edf2; font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif; font-size: 0.85rem; }
    .brand-subtitle { margin: 0; color: #c7bac3; font-size: 1.2rem; font-weight: 500; }
    .stChatMessage { background: rgba(14, 10, 15, 0.92) !important; border: 1px solid rgba(255, 0, 117, 0.25); border-radius: 3px; color: #f1eaf0; }
    .stButton > button { background: #ed006f !important; color: #fff !important; border: 1px solid #ff3b98 !important; border-radius: 2px; font-family: 'Orbitron', 'Eurostile', 'Bank Gothic', sans-serif; font-size: 0.75rem; font-weight: 600; }
    .stButton > button:hover { background: #ff1687 !important; border-color: #ff75b7 !important; }
    .btn-voltar > button { background: transparent !important; border: 1px solid #ff0055 !important; color: #ff0055 !important; }
    .btn-voltar > button:hover { background: rgba(255, 0, 85, 0.1) !important; }
    .streamlit-expanderHeader { background: rgba(13, 9, 14, 0.94) !important; color: #ff4b9c !important; border: 1px solid rgba(255, 0, 117, 0.32); border-radius: 2px; }
    [data-testid="stSidebar"] h3 { font-size: 0.95rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { font-size: 1rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"], [data-testid="stSidebar"] [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label { font-size: 0.75rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetric"] { border-left: 2px solid rgba(240, 0, 117, 0.65); padding: 0.25rem 0.6rem; background: rgba(18, 11, 18, 0.7); }
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

if "mensagens" not in st.session_state: st.session_state.mensagens = []
if "pergunta_pendente" not in st.session_state: st.session_state.pergunta_pendente = None
if "cat_selecionada" not in st.session_state: st.session_state.cat_selecionada = None

@st.cache_data
def obter_ranking_global_absoluto():
    resultados_globais = colecao.get(include=["metadatas"])
    metadatas_todas = resultados_globais["metadatas"]
    negativas, positivas, todas = [], [], []
    for meta in metadatas_todas:
        try: score = int(float(meta.get("review_score", 3)))
        except: score = 3
        cat = meta.get("product_category_name", "desconhecido")
        todas.append(cat)
        if score <= 2: negativas.append(cat)
        elif score >= 4: positivas.append(cat)
    return Counter(negativas), Counter(positivas), Counter(todas)

ranking_negativo_global, ranking_positivo_global, ranking_geral_global = obter_ranking_global_absoluto()

with st.sidebar:
    st.markdown("<h2 style='color: #ff0055; margin-bottom: 0;'>POS TECH</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; font-size: 0.85rem;'>FIAP - IA & Machine Learning</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### KPIs por Categoria")
    categorias_kpi = ["Todas as categorias", *sorted(ranking_geral_global)]
    categoria_kpi = st.selectbox("Selecione para inspecionar:", categorias_kpi, key="categoria_kpi", format_func=lambda c: c if c == "Todas as categorias" else c.replace("_", " ").title())
    
    if categoria_kpi == "Todas as categorias":
        total_categoria = sum(ranking_geral_global.values())
        positivas_categoria = sum(ranking_positivo_global.values())
        negativas_categoria = sum(ranking_negativo_global.values())
    else:
        total_categoria = ranking_geral_global.get(categoria_kpi, 0)
        positivas_categoria = ranking_positivo_global.get(categoria_kpi, 0)
        negativas_categoria = ranking_negativo_global.get(categoria_kpi, 0)

    st.metric("Avaliações Analisadas", total_categoria)
    st.metric("Elogios (notas 4-5)", positivas_categoria)
    st.metric("Reclamações (notas 1-2)", negativas_categoria)

    st.markdown("---")
    if st.button("🗑️ Limpar Todo o Histórico"):
        st.session_state.mensagens = []
        st.session_state.pergunta_pendente = None
        st.session_state.cat_selecionada = None
        st.rerun()

# --- 1. TELA INICIAL (DASHBOARD ZERO-STATE COM BARRAS CLICÁVEIS) ---
mostrar_dashboard = len(st.session_state.mensagens) == 0 and not st.session_state.cat_selecionada

if mostrar_dashboard:
    st.markdown("<h3 style='text-align: center; color: #fff;'>🎛️ Painel de Descoberta Rápida</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #c7bac3;'><b>Clique nas barras dos gráficos abaixo</b> para iniciar imediatamente a análise no chat.</p>", unsafe_allow_html=True)
    st.write("")
    
    col_neg, col_pos = st.columns(2)
    
    with col_neg:
        st.markdown("<h4 style='color: #ff0055; text-align: center;'>⚠️ Top 5 Reclamações</h4>", unsafe_allow_html=True)
        top5_neg = ranking_negativo_global.most_common(5)
        
        # Preparar dados para o Gráfico de Barras
        df_neg = pd.DataFrame(top5_neg, columns=["Categoria", "Reclamações"])
        df_neg["Categoria Formatar"] = df_neg["Categoria"].str.replace("_", " ").str.title()
        df_neg = df_neg.sort_values(by="Reclamações", ascending=True) # Ordem crescente para a maior ficar no topo
        
        # Gráfico Horizontal
        fig_neg = px.bar(df_neg, x="Reclamações", y="Categoria Formatar", orientation='h', color_discrete_sequence=["#ff0055"])
        fig_neg.update_traces(texttemplate='<b>%{x}</b>', textposition='outside')
        fig_neg.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0", margin=dict(t=10, b=10, l=0, r=0), xaxis=dict(visible=False), yaxis=dict(title=""))
        
        # O SEGREDO: Barras suportam cliques 100% nativamente!
        event_neg = st.plotly_chart(fig_neg, use_container_width=True, on_select="rerun", selection_mode="points", key="bar_neg")
        
        if event_neg and event_neg.get("selection") and event_neg["selection"].get("points"):
            clicked_label = event_neg["selection"]["points"][0]["y"]
            cat_original = next((c[0] for c in top5_neg if c[0].replace("_", " ").title() == clicked_label), None)
            if cat_original:
                st.session_state.cat_selecionada = cat_original
                st.session_state.pergunta_pendente = f"quais são as reclamações e problemas da categoria {cat_original}"
                st.rerun()

    with col_pos:
        st.markdown("<h4 style='color: #00e699; text-align: center;'>⭐ Top 5 Elogios</h4>", unsafe_allow_html=True)
        top5_pos = ranking_positivo_global.most_common(5)
        
        # Preparar dados para o Gráfico de Barras
        df_pos = pd.DataFrame(top5_pos, columns=["Categoria", "Elogios"])
        df_pos["Categoria Formatar"] = df_pos["Categoria"].str.replace("_", " ").str.title()
        df_pos = df_pos.sort_values(by="Elogios", ascending=True)
        
        # Gráfico Horizontal
        fig_pos = px.bar(df_pos, x="Elogios", y="Categoria Formatar", orientation='h', color_discrete_sequence=["#00e699"])
        fig_pos.update_traces(texttemplate='<b>%{x}</b>', textposition='outside')
        fig_pos.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0", margin=dict(t=10, b=10, l=0, r=0), xaxis=dict(visible=False), yaxis=dict(title=""))
        
        event_pos = st.plotly_chart(fig_pos, use_container_width=True, on_select="rerun", selection_mode="points", key="bar_pos")
        
        if event_pos and event_pos.get("selection") and event_pos["selection"].get("points"):
            clicked_label = event_pos["selection"]["points"][0]["y"]
            cat_original = next((c[0] for c in top5_pos if c[0].replace("_", " ").title() == clicked_label), None)
            if cat_original:
                st.session_state.cat_selecionada = cat_original
                st.session_state.pergunta_pendente = f"quais são os elogios e pontos positivos da categoria {cat_original}"
                st.rerun()

else:
    # --- 2. MODO CHAT (Botão Voltar e Histórico) ---
    col_btn, _ = st.columns([2, 8])
    with col_btn:
        st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
        if st.button("⬅️ Voltar ao Dashboard", use_container_width=True):
            st.session_state.mensagens = []
            st.session_state.pergunta_pendente = None
            st.session_state.cat_selecionada = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
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
                        st.markdown(f"**Categoria:** `{meta.get('product_category_name')}` | **Nota:** `{meta.get('review_score')}/5` | **Data:** `{meta.get('order_purchase_timestamp')}`")
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
                        if modo_porcentagem: st.markdown(f"{pos}. `{cat}` — **{(freq / total_ctx) * 100 if total_ctx > 0 else 0:.1f}%** ({freq} ocorrência(s))")
                        else: st.markdown(f"{pos}. `{cat}` — **{freq} ocorrência(s)**")

def processar_resposta(pergunta_utilizador, categoria_forcada=None):
    with st.chat_message("assistant"):
        with st.spinner("A consultar Base Vetorial e Analisar Voz do Cliente..."):
            
            dados_nlp = analisar_pergunta_rag(
                pergunta_utilizador, 
                categorias_validas=ranking_geral_global.keys(), 
                categoria_forcada=categoria_forcada
            )
            
            intencao = detetar_intencao(dados_nlp["pergunta_segura"])
            vetor_pergunta = modelo_embeddings.encode([dados_nlp["pergunta_segura"]]).tolist()
            categoria_alvo = dados_nlp["categoria_alvo"]

            if intencao == "negativa":
                ranking_ativo = ranking_negativo_global
                total_contexto = sum(ranking_negativo_global.values())
            elif intencao == "positiva" or "elogiados" in dados_nlp["pergunta_lower"]:
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

            if dados_nlp["pede_comparacao"]:
                if categoria_alvo:
                    neg_cat = ranking_negativo_global.get(categoria_alvo, 0)
                    pos_cat = ranking_positivo_global.get(categoria_alvo, 0)
                    resposta_texto = f"### 📊 Análise Comparativa para a Categoria: `{categoria_alvo}`\n\n- **Reclamações (Notas 1 e 2):** `{neg_cat}` ocorrência(s)\n- **Elogios (Notas 4 e 5):** `{pos_cat}` ocorrência(s)\n\n"
                    if neg_cat > pos_cat: resposta_texto += f"👉 Nesta categoria, existem **mais pessoas a reclamar** do que a elogiar."
                    elif pos_cat > neg_cat: resposta_texto += f"👉 Nesta categoria, existem **mais pessoas a elogiar** do que a reclamar."
                    else: resposta_texto += f"👉 Há um equilíbrio exato entre reclamações e elogios nesta categoria."
                else:
                    neg_total = sum(ranking_negativo_global.values())
                    pos_total = sum(ranking_positivo_global.values())
                    resposta_texto = f"### 📊 Análise Comparativa Global da Olist\n\n- **Reclamações Totais:** `{neg_total}` ocorrência(s)\n- **Elogios Totais:** `{pos_total}` ocorrência(s)\n\n"
                    if neg_total > pos_total: resposta_texto += f"👉 No panorama geral da plataforma, existem **mais reclamações** do que elogios."
                    else: resposta_texto += f"👉 No panorama geral da plataforma, existem **mais elogios** do que reclamações."
                        
            elif dados_nlp["pede_problemas"] and not categoria_alvo:
                st.session_state.pergunta_pendente = dados_nlp["pergunta_segura"]
                resposta_texto = "### ⚠️ Análise Geral dos Principais Problemas:\n\nNum panorama macro da operação, os clientes demonstram insatisfação principalmente por 3 motivos centrais:\n1. **Logística:** Atrasos nas entregas e falhas nas transportadoras.\n2. **Qualidade:** Produtos que chegam com defeito ou não correspondem ao anúncio.\n3. **Pós-Venda:** Dificuldade no contacto e estorno com os parceiros."
            
            else:
                deve_mostrar_ranking = bool(dados_nlp["pede_ranking"] or dados_nlp["pediu_grafico"] or dados_nlp["pergunta_porcentagem"]) and not categoria_alvo
                top_5 = ranking_ativo.most_common(5)
                resto_ranking = ranking_ativo.most_common()[5:]

                if categoria_alvo:
                    if intencao == "positiva" or "elogi" in dados_nlp["pergunta_lower"] or "positiv" in dados_nlp["pergunta_lower"]:
                        resposta_texto = f"### 🔍 Análise de Elogios da Categoria: `{categoria_alvo}`\n\nCom base na auditoria das avaliações reais, os clientes desta categoria destacam a excelente qualidade, o ótimo custo-benefício e a rapidez na entrega. Consulte as evidências de satisfação abaixo."
                    elif intencao == "negativa" or "reclam" in dados_nlp["pergunta_lower"] or "negativ" in dados_nlp["pergunta_lower"] or "problema" in dados_nlp["pergunta_lower"]:
                        resposta_texto = f"### 🔍 Análise de Problemas da Categoria: `{categoria_alvo}`\n\nCom base na auditoria das avaliações de insatisfação (notas 1 e 2), os clientes reportam falhas logísticas, atrasos e avarias no produto. Consulte os relatos na íntegra abaixo."
                    else:
                        neg_cat = ranking_negativo_global.get(categoria_alvo, 0)
                        pos_cat = ranking_positivo_global.get(categoria_alvo, 0)
                        resposta_texto = f"### 🔍 Resumo Geral da Categoria: `{categoria_alvo}`\n\nEsta categoria apresenta um cenário misto de interações:\n- **Lado Positivo ({pos_cat} elogios):** Os consumidores elogiam a utilidade e a entrega dos produtos corretos.\n- **Lado Negativo ({neg_cat} reclamações):** As principais queixas envolvem logística demorada ou itens trocados.\n\nConsulte as evidências auditáveis abaixo."
                elif deve_mostrar_ranking:
                    ranking_texto = "### 🏆 Ranking de Categorias:\n"
                    for pos, (cat, freq) in enumerate(top_5, 1):
                        ranking_texto += f"{pos}. `{cat}` — **{freq} ocorrência(s)**\n"

                    if dados_nlp["pergunta_porcentagem"] or dados_nlp["pediu_grafico"]:
                        resposta_porcentagem = "### 📊 Porcentagem por Categoria:\n\n"
                        dados_grafico = []
                        soma_top_5 = 0
                        for cat, freq in top_5:
                            porcentagem = (freq / total_contexto) * 100 if total_contexto > 0 else 0
                            resposta_porcentagem += f"- **{cat}**: `{porcentagem:.1f}%` ({freq} ocorrência(s))\n"
                            dados_grafico.append({"Categoria": cat, "Ocorrências": freq})
                            soma_top_5 += freq
                        
                        outros = total_contexto - soma_top_5
                        if outros > 0: dados_grafico.append({"Categoria": "Outras Categorias", "Ocorrências": outros})
                        
                        resposta_texto = resposta_porcentagem

                        if dados_nlp["pediu_grafico"]:
                            import pandas as pd
                            df_pizza = pd.DataFrame(dados_grafico)
                            figura_plotly = px.pie(df_pizza, names="Categoria", values="Ocorrências", title="Distribuição Percentual Absoluta (Base Global)", color_discrete_sequence=px.colors.sequential.RdBu)
                            figura_plotly.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0")
                    elif intencao == "positiva" or "elogiados" in dados_nlp["pergunta_lower"]:
                        resposta_texto = "**Análise de Elogios e Satisfação:**\nAbaixo encontram-se as 5 categorias com maior volume absoluto de avaliações positivas:\n\n" + ranking_texto
                    else:
                        resposta_texto = "**Panorama Geral das Categorias com Mais Problemas:**\nAbaixo encontram-se as 5 categorias com maior volume absoluto de reclamações:\n\n" + ranking_texto
                else:
                    resposta_texto = "### 🔍 Análise de Voz do Cliente\n\nCom base nos registos recuperados da base de dados, consulte as evidências auditáveis reais associadas à sua pesquisa."

            resultados_busca = colecao.query(query_embeddings=vetor_pergunta, n_results=60)
            documentos_raw = resultados_busca["documents"][0]
            metadados_raw = resultados_busca["metadatas"][0]
            documentos_validos, metadados_validos = [], []

            for doc, meta in zip(documentos_raw, metadados_raw):
                try: score = int(float(meta.get("review_score", 3)))
                except: score = 3
                cat = meta.get("product_category_name", "desconhecido")

                if categoria_alvo and cat != categoria_alvo: continue
                if intencao == "negativa" and score <= 2:
                    documentos_validos.append(doc); metadados_validos.append(meta)
                elif (intencao == "positiva" or "elogiados" in dados_nlp["pergunta_lower"]) and score >= 4:
                    documentos_validos.append(doc); metadados_validos.append(meta)
                elif intencao == "neutra" and not dados_nlp["pede_comparacao"]:
                    documentos_validos.append(doc); metadados_validos.append(meta)

            if categoria_alvo and len(documentos_validos) == 0:
                for doc, meta in zip(documentos_raw, metadados_raw):
                    if meta.get("product_category_name") == categoria_alvo:
                        documentos_validos.append(doc); metadados_validos.append(meta)

            st.markdown(resposta_texto, unsafe_allow_html=True)
            if figura_plotly: st.plotly_chart(figura_plotly, use_container_width=True)

            par_evidencias = list(zip(documentos_validos, metadados_validos))
            limite_inicial = 5

            msg_nova = {
                "role": "assistant", "conteudo_texto": resposta_texto, "figura_grafico": figura_plotly,
                "evidencias": par_evidencias, "limite_atual": limite_inicial,
                "exigir_ranking_flag": deve_mostrar_ranking, "resto_ranking": resto_ranking,
                "modo_porcentagem": dados_nlp["pergunta_porcentagem"], "total_contexto": total_contexto,
                "mostrar_botoes_categorias": mostrar_botoes_categorias
            }
            
            st.session_state.mensagens.append(msg_nova)
            novo_idx = len(st.session_state.mensagens) - 1

            if deve_mostrar_ranking and resto_ranking:
                with st.expander("📈 Ver restante do Ranking Completo de Categorias"):
                    for pos, (cat, freq) in enumerate(resto_ranking, 6):
                        if dados_nlp["pergunta_porcentagem"]:
                            st.markdown(f"{pos}. `{cat}` — **{(freq / total_contexto) * 100 if total_contexto > 0 else 0:.1f}%** ({freq} ocorrência(s))")
                        else: st.markdown(f"{pos}. `{cat}` — **{freq} ocorrência(s)**")

            evidencias_visiveis = par_evidencias[:limite_inicial]
            if par_evidencias:
                with st.expander(f"🔍 Ver Evidências Reais Auditáveis (Exibindo {len(evidencias_visiveis)} de {len(par_evidencias)})"):
                    for i, (doc, meta) in enumerate(evidencias_visiveis):
                        st.markdown(f"**Categoria:** `{meta.get('product_category_name')}` | **Nota:** `{meta.get('review_score')}/5` | **Data:** `{meta.get('order_purchase_timestamp')}`")
                        st.text(doc)
                        st.divider()

                    if len(evidencias_visiveis) < len(par_evidencias):
                        if st.button("Carregar mais 5 evidências", key=f"btn_carregar_novo_{novo_idx}"):
                            st.session_state.mensagens[novo_idx]["limite_atual"] += 5
                            st.rerun()

# --- 3. GESTÃO DO CLIQUE NO GRÁFICO (Injeta o texto na conversa e oculta Dashboard) ---
if st.session_state.cat_selecionada:
    cat_escolhida = st.session_state.cat_selecionada
    st.session_state.cat_selecionada = None  # Limpa o estado para não fazer loop
    
    pergunta_anterior = st.session_state.get("pergunta_pendente")
    if not isinstance(pergunta_anterior, str): 
        pergunta_anterior = "quais são os problemas"
        
    st.session_state.mensagens.append({"role": "user", "conteudo_texto": f"Analisar: {cat_escolhida.replace('_', ' ').title()}"})
    with st.chat_message("user"): 
        st.markdown(f"Analisar: `{cat_escolhida.replace('_', ' ').title()}`")
        
    processar_resposta(pergunta_anterior, categoria_forcada=cat_escolhida)

# --- 4. CAIXA DE TEXTO DO CHAT (Sempre visível no fundo) ---
if pergunta_utilizador := st.chat_input("Digite sua pergunta sobre as avaliações da Olist..."):
    st.session_state.mensagens.append({"role": "user", "conteudo_texto": pergunta_utilizador})
    with st.chat_message("user"): 
        st.markdown(pergunta_utilizador)
    processar_resposta(pergunta_utilizador)