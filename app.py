import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# =========================
# FETCH
# =========================

@st.cache_data
def fetch_html(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    return response.text


def get_soup(html):
    return BeautifulSoup(html, "html.parser")


# =========================
# PARSING
# =========================

def get_review_element(soup):
    selectors = [
        ".review-body",
        ".body-text",
        ".review",
        ".truncate"
    ]

    for selector in selectors:
        el = soup.select_one(selector)
        if el and len(el.get_text(strip=True)) > 80:
            return el

    return None


def get_username(soup):
    user = soup.select_one("a.name")
    return user.get_text().strip() if user else "Desconhecido"


def get_likes_given(soup):
    liked = soup.select("section.liked-reviews li")
    return len(liked)


# =========================
# ANÁLISE DE TEXTO
# =========================

def analyze_text(review_element):
    text = review_element.get_text()

    words = text.split()
    word_count = len(words)

    sentences = text.count('.') + text.count('!') + text.count('?')
    sentences = max(sentences, 1)

    avg_words_per_sentence = round(word_count / sentences, 1)

    reading_time = round(word_count / 200, 1)

    return {
        "word_count": word_count,
        "sentences": sentences,
        "avg_sentence": avg_words_per_sentence,
        "reading_time": reading_time
    }


# =========================
# CLASSIFICAÇÃO DO REVIEW
# =========================

def classify_review(word_count):
    if word_count < 80:
        return "Curto"
    elif word_count < 250:
        return "Médio"
    else:
        return "Longo"


# =========================
# UI
# =========================

st.title("📊 Letterboxd Review Analyzer")

DEBUG = st.sidebar.checkbox("Modo Debug")

url = st.text_input("Cole a URL do Letterboxd:")

if st.button("Analisar"):

    if not url:
        st.warning("Insira uma URL válida")
        st.stop()

    st.info("Carregando página...")

    html = fetch_html(url)
    soup = get_soup(html)

    review_element = get_review_element(soup)

    if not review_element:
        st.error("❌ Não foi possível identificar um review nessa página")
        st.stop()

    usuario = get_username(soup)
    likes_dados = get_likes_given(soup)

    analysis = analyze_text(review_element)

    tipo = classify_review(analysis["word_count"])

    # =========================
    # MÉTRICAS
    # =========================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Palavras", analysis["word_count"])
    col2.metric("Tempo leitura (min)", analysis["reading_time"])
    col3.metric("Likes dados", likes_dados)
    col4.metric("Tipo de review", tipo)

    # =========================
    # DETALHES
    # =========================

    st.subheader("📋 Estrutura do texto")

    st.write(f"**Sentenças estimadas:** {analysis['sentences']}")
    st.write(f"**Média de palavras por sentença:** {analysis['avg_sentence']}")

    # =========================
    # GRÁFICO
    # =========================

    st.subheader("📊 Distribuição")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Palavras", "Sentenças"],
        y=[analysis["word_count"], analysis["sentences"]]
    ))

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INSIGHT SIMPLES (SEGURO)
    # =========================

    st.subheader("🧠 Leitura do review")

    if tipo == "Longo":
        st.success("Review detalhado, com maior profundidade")
    elif tipo == "Médio":
        st.info("Review equilibrado")
    else:
        st.warning("Review curto, mais direto")

    # =========================
    # DEBUG
    # =========================

    if DEBUG:
        st.sidebar.write("Usuário:", usuario)
        st.sidebar.write("Texto (preview):")
        st.sidebar.write(review_element.get_text()[:300])