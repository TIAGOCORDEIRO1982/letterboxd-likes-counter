import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from collections import Counter
import re
import math

st.set_page_config(layout="wide")

# =========================
# CONFIG
# =========================

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# =========================
# MENU
# =========================

st.sidebar.title("Menu")

opcao = st.sidebar.selectbox(
    "Escolha a análise",
    [
        "Análise de Review",
        "Em breve"
    ]
)

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
    selectors = [".review-body", ".body-text", ".review", ".truncate"]

    for selector in selectors:
        el = soup.select_one(selector)
        if el and len(el.get_text(strip=True)) > 80:
            return el

    return None


def get_username(soup):
    user = soup.select_one("a.name")
    return user.get_text().strip() if user else "Desconhecido"


def get_likes_given(soup):
    return len(soup.select("section.liked-reviews li"))


# =========================
# TEXTO
# =========================

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)

    stopwords = {
        "the","a","and","to","of","in","is","it","that","this","for","on",
        "com","de","da","do","e","o","a","que","um","uma","em"
    }

    words = [w for w in text.split() if w not in stopwords and len(w) > 3]

    return words


def get_top_words(text, n=12):
    words = clean_text(text)
    counts = Counter(words)
    return counts.most_common(n)


# =========================
# BUBBLE CHART MELHORADO
# =========================

def create_bubble_chart(word_counts):
    words = [w for w, _ in word_counts]
    values = [v for _, v in word_counts]

    max_val = max(values)

    # tamanho proporcional mais equilibrado
    sizes = [50 + (v / max_val) * 100 for v in values]

    x = []
    y = []

    # layout espiral compacta (mais próximo)
    for i in range(len(words)):
        angle = i * 0.6
        radius = 0.5 + i * 0.15

        x.append(math.cos(angle) * radius)
        y.append(math.sin(angle) * radius)

    colors = [
        "#A78BFA", "#60A5FA", "#34D399",
        "#FBBF24", "#F87171", "#F472B6",
        "#38BDF8", "#818CF8", "#4ADE80",
        "#FB923C", "#C084FC", "#22D3EE"
    ]

    # texto com contagem
    labels = [f"{w}<br>{v}x" for w, v in word_counts]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers+text',
        text=labels,
        textposition="middle center",
        marker=dict(
            size=sizes,
            color=colors[:len(words)],
            line=dict(width=0)
        ),
        textfont=dict(
            size=13,
            color="white"
        ),
        hoverinfo='text'
    ))

    fig.update_layout(
        template="plotly_dark",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        height=550,
        margin=dict(l=0, r=0, t=20, b=0)
    )

    return fig


# =========================
# ANÁLISE DE TEXTO
# =========================

def analyze_text(review_element):
    text = review_element.get_text()

    words = text.split()
    word_count = len(words)

    sentences = text.count('.') + text.count('!') + text.count('?')
    sentences = max(sentences, 1)

    avg_words = round(word_count / sentences, 1)
    reading_time = round(word_count / 200, 1)

    return {
        "text": text,
        "word_count": word_count,
        "sentences": sentences,
        "avg_sentence": avg_words,
        "reading_time": reading_time
    }


def classify_review(word_count):
    if word_count < 80:
        return "Curto"
    elif word_count < 250:
        return "Médio"
    return "Longo"


# =========================
# UI
# =========================

if opcao == "Análise de Review":

    st.title("📊 Letterboxd Review Analyzer")

    url = st.text_input("Cole a URL do Letterboxd:")

    if st.button("Analisar"):

        if not url:
            st.warning("Insira uma URL válida")
            st.stop()

        html = fetch_html(url)
        soup = get_soup(html)

        review_element = get_review_element(soup)

        if not review_element:
            st.error("❌ Review não encontrado")
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
        col2.metric("Tempo leitura", analysis["reading_time"])
        col3.metric("Likes dados", likes_dados)
        col4.metric("Tipo", tipo)

        # =========================
        # TEXTO
        # =========================

        st.subheader("📋 Estrutura do texto")

        st.write(f"Sentenças: {analysis['sentences']}")
        st.write(f"Média por frase: {analysis['avg_sentence']}")

        # =========================
        # BUBBLE WORD CLOUD
        # =========================

        st.subheader("☁️ Nuvem de palavras")

        top_words = get_top_words(analysis["text"])
        fig_wc = create_bubble_chart(top_words)

        st.plotly_chart(fig_wc, use_container_width=True)


elif opcao == "Em breve":
    st.title("🚧 Em breve")
    st.write("Novas análises serão adicionadas aqui.")