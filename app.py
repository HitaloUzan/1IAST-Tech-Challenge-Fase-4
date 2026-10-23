import json
import os
import re

import pandas as pd
import plotly.express as px
import streamlit as st
from sentence_transformers import SentenceTransformer

from src import llm as llm_config
from src import rag_pipeline as rp
from src.analytics import ReviewAnalytics
from src.config import EMBEDDING_MODEL
from src.vector_store import get_collection

MAX_LLM_CALLS_PER_SESSION = int(os.getenv("MAX_LLM_CALLS_PER_SESSION", "20"))
EVIDENCE_PAGE_SIZE = 5
EXAMPLE_QUESTIONS = [
    "Quais são os principais problemas relatados pelos clientes em suas avaliações?",
    "O que os clientes relatam sobre problemas relacionados à entrega?",
    "Quais aspectos da experiência de compra são mais elogiados pelos clientes?",
    "Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?",
    "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?",
    "Qual a capital da França?",
]

st.set_page_config(
    page_title="Tech Challenge - Fase 4 | FIAP Pós Tech",
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
    .streamlit-expanderHeader { background: rgba(13, 9, 14, 0.94) !important; color: #ff4b9c !important; border: 1px solid rgba(255, 0, 117, 0.32); border-radius: 2px; }
    [data-testid="stSidebar"] h3 { font-size: 0.95rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { font-size: 1rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"], [data-testid="stSidebar"] [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label { font-size: 0.75rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetric"] { border-left: 2px solid rgba(240, 0, 117, 0.65); padding: 0.25rem 0.6rem; background: rgba(18, 11, 18, 0.7); }
    .cite { color: #ff4b9c; font-weight: 700; }
    .evidence-cited { border-left: 3px solid #ff4b9c; padding-left: 0.6rem; }
    .evidence-other { border-left: 3px solid rgba(255, 255, 255, 0.15); padding-left: 0.6rem; }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Carregando modelo de embeddings, base vetorial e LLM...")
def load_engine():
  analytics = ReviewAnalytics()
  pipeline = rp.VoCPipeline.with_configured_llm(
      SentenceTransformer(EMBEDDING_MODEL), get_collection(), analytics.categories
  )
  return analytics, pipeline


analytics, pipeline = load_engine()
llm_enabled = pipeline.generator is not None


def pretty(category: str) -> str:
  return category.replace("_", " ").title()


def init_state():
  defaults = {"messages": [], "pending": None, "llm_calls": 0}
  for key, value in defaults.items():
    st.session_state.setdefault(key, value)


init_state()


def reset_conversation():
  st.session_state.messages = []
  st.session_state.pending = None
  for key in ("bar_negativa", "bar_positiva"):
    st.session_state.pop(key, None)


st.markdown("""
    <div class="brand-lockup">
        <div class="brand-mark">FIAP</div>
        <p class="brand-kicker">POS TECH · FASE 4</p>
        <p class="brand-subtitle">Voice of Customer Intelligence · Olist</p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR: KPIs, filtros e status do modelo ---
with st.sidebar:
  st.markdown("<h2 style='color: #ff0055; margin-bottom: 0;'>POS TECH</h2>", unsafe_allow_html=True)
  st.markdown("<p style='color: #888; font-size: 0.85rem;'>FIAP - IA & Machine Learning</p>", unsafe_allow_html=True)
  st.markdown("---")

  st.markdown("### Modelo de linguagem")
  if llm_enabled:
    remaining = max(MAX_LLM_CALLS_PER_SESSION - st.session_state.llm_calls, 0)
    st.success(f"Ativo: {pipeline.generator.label}")
    st.caption(f"Perguntas com geração restantes nesta sessão: {remaining}")
  else:
    st.warning(
        "Modo só busca: nenhuma chave de LLM configurada. As evidências são recuperadas"
        " normalmente, sem a resposta gerada. Veja o README para configurar."
    )

  st.markdown("### KPIs por categoria")
  kpi_options = ["Todas as categorias", *[c for c in analytics.categories if c != "desconhecido"]]
  kpi_category = st.selectbox(
      "Selecione para inspecionar:", kpi_options, key="kpi_category",
      format_func=lambda c: c if c == "Todas as categorias" else pretty(c),
  )
  counts = analytics.counts(None if kpi_category == "Todas as categorias" else kpi_category)
  st.metric("Avaliações com texto", f"{counts.total:,}".replace(",", "."))
  st.metric("Elogios (notas 4-5)", f"{counts.positive:,}".replace(",", "."))
  st.metric("Reclamações (notas 1-2)", f"{counts.negative:,}".replace(",", "."))

  st.markdown("### Filtros da busca")
  st.caption("Somam-se aos filtros detectados automaticamente na pergunta.")
  score_filter = st.selectbox(
      "Nota", ["Detectar pela pergunta", "Notas 1-2", "Nota 3", "Notas 4-5"], key="score_filter"
  )
  category_filter = st.selectbox(
      "Categoria", ["Detectar pela pergunta", *[c for c in analytics.categories if c != "desconhecido"]],
      key="category_filter", format_func=lambda c: c if c.startswith("Detectar") else pretty(c),
  )
  year_filter = st.selectbox("Ano da compra", ["Todos", 2016, 2017, 2018], key="year_filter")
  late_filter = st.checkbox("Só entregas atrasadas ou não entregues", key="late_filter")

  st.markdown("---")
  if st.button("🗑️ Limpar histórico", width="stretch"):
    reset_conversation()
    st.rerun()


def sidebar_filters() -> dict:
  filters = {}
  if score_filter == "Notas 1-2":
    filters["score_max"] = 2
  elif score_filter == "Nota 3":
    filters.update(score_min=3, score_max=3)
  elif score_filter == "Notas 4-5":
    filters["score_min"] = 4
  if not category_filter.startswith("Detectar"):
    filters["category"] = category_filter
  if year_filter != "Todos":
    filters["year"] = int(year_filter)
  if late_filter:
    filters["late_delivery"] = True
  return filters


def ask(question: str, forced_category: str | None = None):
  st.session_state.pending = {"question": question, "category": forced_category}
  st.rerun()


# --- RENDERIZAÇÃO DAS RESPOSTAS ---
def highlight_citations(text: str) -> str:
  return re.sub(r"\[R(\d+)\]", r"<span class='cite'>[R\1]</span>", text)


def render_evidences(answer: rp.RAGAnswer, message_index: int):
  evidences = answer.evidences
  if not evidences:
    return
  order = [i for i in range(1, len(evidences) + 1) if i in answer.cited]
  order += [i for i in range(1, len(evidences) + 1) if i not in answer.cited]
  limit_key = f"evidence_limit_{message_index}"
  limit = st.session_state.get(limit_key, EVIDENCE_PAGE_SIZE)
  title = f"🔍 Evidências recuperadas ({len(evidences)}"
  title += f", {len(answer.cited)} citadas na resposta)" if answer.status == rp.ANSWERED else ")"
  with st.expander(title, expanded=answer.status != rp.ANSWERED):
    for n in order[:limit]:
      evidence = evidences[n - 1]
      meta = evidence.metadata
      cited = n in answer.cited
      delivery = meta.get("delivery_status", "").replace("_", " ")
      if meta.get("delivery_status") == "atrasado" and meta.get("delivery_delay_days") is not None:
        delivery += f" ({meta['delivery_delay_days']} dia(s))"
      badge = " · <span class='cite'>citada</span>" if cited else ""
      st.markdown(
          f"<div class='{'evidence-cited' if cited else 'evidence-other'}'>"
          f"<b>[R{n}]</b>{badge} · nota <b>{meta.get('review_score')}/5</b> · "
          f"{pretty(meta.get('product_category_name', ''))} · compra {meta.get('purchase_month')} · "
          f"entrega {delivery} · similaridade {evidence.similarity:.2f}<br/>"
          f"<span style='color:#888;font-size:0.8rem'>review_id {evidence.review_id}</span></div>",
          unsafe_allow_html=True,
      )
      st.text(evidence.text)
    if limit < len(order):
      if st.button("Carregar mais 5 evidências", key=f"more_{message_index}"):
        st.session_state[limit_key] = limit + EVIDENCE_PAGE_SIZE
        st.rerun()


def render_trace(answer: rp.RAGAnswer):
  parsed = answer.parsed
  with st.expander("⚙️ Como a pergunta foi processada"):
    st.markdown(
        f"- **Pergunta normalizada:** `{parsed.normalized}`\n"
        f"- **Consulta semântica (sem palavras de enquadramento):** `{parsed.semantic_query}`\n"
        f"- **Rota:** `{parsed.route}` · **Sentimento detectado:** `{parsed.sentiment}`\n"
        f"- **Filtros:** {', '.join(parsed.describe_filters()) or 'nenhum'}\n"
        f"- **Dentro do escopo:** {'sim' if parsed.in_domain else 'não'}"
    )
    retrieval = answer.retrieval
    if retrieval:
      st.markdown(
          f"- **Cláusula `where` enviada ao ChromaDB:** `{json.dumps(retrieval.where, ensure_ascii=False)}`\n"
          f"- **Candidatos:** {len(retrieval.candidates)} · **acima do limiar** "
          f"(distância > {retrieval.max_distance}): {len(retrieval.rejected)} · "
          f"**selecionados por MMR:** {len(retrieval.evidences)}"
      )
      if retrieval.candidates:
        selected = {e.review_id for e in retrieval.evidences}
        table = pd.DataFrame([
            {
                "distância": round(c.distance, 3),
                "situação": "no contexto" if c.review_id in selected
                else ("descartada: pouco relevante" if c.distance > retrieval.max_distance
                      else "descartada: redundante (MMR)"),
                "nota": c.metadata.get("review_score"),
                "texto": c.text[:90],
            }
            for c in retrieval.candidates
        ])
        st.dataframe(table, hide_index=True, width="stretch")
    if answer.llm_label:
      st.markdown(f"- **Modelo:** `{answer.llm_label}`")
    if answer.user_prompt:
      st.markdown("**Contexto enviado ao modelo:**")
      st.code(answer.user_prompt, language="text")


def render_ranking(answer: rp.RAGAnswer):
  parsed = answer.parsed
  sentiment = parsed.sentiment
  label = {"negativa": "reclamações (notas 1-2)", "positiva": "elogios (notas 4-5)"}.get(sentiment, "avaliações")
  table = analytics.ranking(sentiment)
  top = table.head(10).copy()
  st.markdown(f"### Ranking de categorias por {label}")
  st.caption(
      "Contagem exata sobre as 42.370 avaliações com texto (não é gerada pelo modelo). "
      "A taxa na categoria compara categorias de tamanhos diferentes de forma justa."
  )
  top["Categoria"] = top["category"].map(pretty)
  top["% do total"] = (top["share_of_sentiment"] * 100).round(1)
  top["Taxa na categoria (%)"] = (top["rate_in_category"] * 100).round(1)
  st.dataframe(
      top[["Categoria", "reviews", "% do total", "Taxa na categoria (%)", "category_total"]].rename(
          columns={"reviews": label.split(" (")[0].capitalize(), "category_total": "Avaliações da categoria"}
      ),
      hide_index=True, width="stretch",
  )
  if parsed.wants_chart:
    others = table.iloc[10:]["reviews"].sum()
    pie = pd.concat([top[["Categoria", "reviews"]], pd.DataFrame([{"Categoria": "Outras", "reviews": others}])])
    fig = px.pie(pie, names="Categoria", values="reviews", color_discrete_sequence=px.colors.sequential.RdPu_r)
  else:
    fig = px.bar(
        top.sort_values("reviews"), x="reviews", y="Categoria", orientation="h",
        color_discrete_sequence=["#ff0055" if sentiment == "negativa" else "#00e699"],
    )
    fig.update_layout(xaxis_title="", yaxis_title="")
  fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0",
                    margin=dict(t=10, b=10, l=0, r=0))
  st.plotly_chart(fig, width="stretch")


def render_comparison(answer: rp.RAGAnswer):
  category = answer.parsed.category
  counts = analytics.counts(category)
  st.markdown(f"### Comparação na categoria {pretty(category)}")
  cols = st.columns(3)
  cols[0].metric("Reclamações (1-2)", counts.negative, f"{counts.negative / counts.total:.1%} da categoria", delta_color="off")
  cols[1].metric("Neutras (3)", counts.neutral, f"{counts.neutral / counts.total:.1%} da categoria", delta_color="off")
  cols[2].metric("Elogios (4-5)", counts.positive, f"{counts.positive / counts.total:.1%} da categoria", delta_color="off")
  overall = analytics.counts()
  verdict = "mais elogios do que reclamações" if counts.positive > counts.negative else "mais reclamações do que elogios"
  st.markdown(
      f"Nesta categoria há **{verdict}**. A taxa de reclamação é **{counts.negative / counts.total:.1%}**, "
      f"contra **{overall.negative / overall.total:.1%}** na base inteira."
  )
  st.caption("Contagem exata sobre todas as avaliações com texto da categoria. Para entender os motivos, pergunte por exemplo: "
             f"\"Quais são as reclamações sobre {pretty(category).lower()}?\"")


def render_answer(answer: rp.RAGAnswer, message_index: int):
  status = answer.status
  if status == rp.ANALYTICS:
    if answer.parsed.route == "comparison":
      render_comparison(answer)
    else:
      render_ranking(answer)
    return

  if status == rp.ANSWERED:
    st.markdown(highlight_citations(answer.text), unsafe_allow_html=True)
    if answer.has_uncited_answer:
      st.warning("O modelo respondeu sem citar nenhuma avaliação. Confira as evidências antes de usar esta resposta.")
  elif status in (rp.NO_EVIDENCE, rp.OUT_OF_SCOPE, rp.LLM_REFUSED):
    st.warning(answer.text)
  elif status == rp.RETRIEVAL_ONLY:
    reason = ("limite de perguntas com geração desta sessão atingido"
              if llm_enabled else "nenhuma chave de LLM configurada")
    st.info(f"Modo só busca ({reason}). Abaixo estão as avaliações mais relevantes que seriam enviadas ao modelo.")
  elif status == rp.LLM_ERROR:
    st.error(f"O modelo de linguagem falhou ({answer.error[:200]}). As evidências recuperadas seguem abaixo.")

  render_evidences(answer, message_index)
  render_trace(answer)


def run_question(question: str, forced_category: str | None):
  use_llm = llm_enabled and st.session_state.llm_calls < MAX_LLM_CALLS_PER_SESSION
  with st.spinner("Buscando avaliações e gerando a resposta..."):
    answer = pipeline.answer(question, forced_category, sidebar_filters(), use_llm=use_llm)
  if answer.status in (rp.ANSWERED, rp.LLM_REFUSED, rp.LLM_ERROR):
    st.session_state.llm_calls += 1
  return answer


# --- 1. TELA INICIAL (PAINEL COM BARRAS CLICÁVEIS) ---
show_dashboard = not st.session_state.messages and not st.session_state.pending

if show_dashboard:
  st.markdown("<h3 style='text-align: center; color: #fff;'>🎛️ Painel de Descoberta Rápida</h3>", unsafe_allow_html=True)
  st.markdown(
      "<p style='text-align: center; color: #c7bac3;'><b>Clique numa barra</b> para investigar os motivos "
      "daquela categoria, use uma pergunta de exemplo ou escreva a sua no campo abaixo.</p>",
      unsafe_allow_html=True,
  )

  col_neg, col_pos = st.columns(2)
  for column, sentiment, title, color, template in (
      (col_neg, "negativa", "⚠️ Top 5 Reclamações", "#ff0055", "Quais são as principais reclamações sobre {}?"),
      (col_pos, "positiva", "⭐ Top 5 Elogios", "#00e699", "O que os clientes mais elogiam em {}?"),
  ):
    with column:
      st.markdown(f"<h4 style='color: {color}; text-align: center;'>{title}</h4>", unsafe_allow_html=True)
      top5 = analytics.ranking(sentiment).head(5).copy()
      top5["Categoria"] = top5["category"].map(pretty)
      fig = px.bar(top5.sort_values("reviews"), x="reviews", y="Categoria", orientation="h",
                   color_discrete_sequence=[color])
      fig.update_traces(texttemplate="<b>%{x}</b>", textposition="outside")
      fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0",
                        margin=dict(t=10, b=10, l=0, r=0), xaxis=dict(visible=False), yaxis=dict(title=""))
      event = st.plotly_chart(fig, width="stretch", on_select="rerun", selection_mode="points", key=f"bar_{sentiment}")
      points = (event or {}).get("selection", {}).get("points", [])
      if points:
        clicked = top5[top5["Categoria"] == points[0]["y"]]["category"]
        if not clicked.empty:
          category = clicked.iloc[0]
          ask(template.format(pretty(category).lower()), category)

  st.markdown("<h4 style='text-align: center; color: #fff;'>Perguntas de exemplo</h4>", unsafe_allow_html=True)
  example_cols = st.columns(2)
  for i, question in enumerate(EXAMPLE_QUESTIONS):
    if example_cols[i % 2].button(question, key=f"example_{i}", width="stretch"):
      ask(question)

else:
  if st.button("⬅️ Voltar ao painel"):
    reset_conversation()
    st.rerun()
  st.markdown("---")

  for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
      if message["role"] == "user":
        st.markdown(message["content"])
      else:
        render_answer(message["answer"], index)

# --- 2. PROCESSAMENTO DA PERGUNTA PENDENTE ---
if st.session_state.pending:
  pending = st.session_state.pending
  st.session_state.pending = None
  st.session_state.messages.append({"role": "user", "content": pending["question"]})
  with st.chat_message("user"):
    st.markdown(pending["question"])
  answer = run_question(pending["question"], pending["category"])
  st.session_state.messages.append({"role": "assistant", "answer": answer})
  with st.chat_message("assistant"):
    render_answer(answer, len(st.session_state.messages) - 1)

# --- 3. CAIXA DE TEXTO DO CHAT ---
if question := st.chat_input("Pergunte sobre as avaliações dos clientes da Olist..."):
  ask(question)
