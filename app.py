import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from collections import Counter
import re
import math
import random

st.set_page_config(layout="wide")

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
    ["Análise de Review", "Em breve"]
)

# =========================
# FETCH
# =========================

@st.cache_data
def fetch_html(url):
    return requests.get(url, headers=HEADERS).text

def get_soup(html):
    return BeautifulSoup(html, "html.parser")

# =========================
# PARSING
# =========================

def get_review_element(soup):
    selectors = [".review-body", ".body-text", ".review", ".truncate"]
    for s in selectors:
        el = soup.select_one(s)
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

    return [w for w in text.split() if w not in stopwords and len(w) > 3]

def get_top_words(text, n=12):
    return Counter(clean_text(text)).most_common(n)

# =========================
# FORCE LAYOUT (CORRIGIDO)
# =========================

def create_bubble_chart(word_counts):

    # ordenar por tamanho
    word_counts = sorted(word_counts, key=lambda x: x[1], reverse=True)

    words = [w for w, _ in word_counts]
    values = [v for _, v in word_counts]

    max_val = max(values)

    sizes = [60 + (v / max_val) * 120 for v in values]
    radii = [s / 2 for s in sizes]

    n = len(words)

    # posições iniciais (todas no centro)
    x = [random.uniform(-0.1, 0.1) for _ in range(n)]
    y = [random.uniform(-0.1, 0.1) for _ in range(n)]

    gap = 5

    # simulação
    for _ in range(200):

        for i in range(n):
            for j in range(i + 1, n):

                dx = x[j] - x[i]
                dy = y[j] - y[i]
                dist = math.sqrt(dx*dx + dy*dy) + 0.001

                min_dist = radii[i] + radii[j] + gap

                if dist < min_dist:
                    force = (min_dist - dist) / dist * 0.5

                    x[i] -= dx * force
                    y[i] -= dy * force
                    x[j] += dx * force
                    y[j] += dy * force

        # força de centralização
        for i in range(1, n):  # mantém a maior fixa no centro
            x[i] += (-x[i]) * 0.05
            y[i] += (-y[i]) * 0.05

    # maior bolha fixa
    x[0], y[0] = 0, 0

    labels = [f"{w}<br>{v}x" for w, v in word_counts]

    colors = [
        "#A78BFA","#60A5FA","#34D399","#FBBF24",
        "#F87171","#F472B6","#38BDF8","#818CF8",
        "#4ADE80","#FB923C","#C084FC","#22D3EE"
    ]

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
        textfont=dict(size=13, color="white"),
        hoverinfo="text"
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
# ANÁLISE
# =========================

def analyze_text(el):
    text = el.get_text()
    words = text.split()

    sentences = text.count('.') + text.count('!') + text.count('?')
    sentences = max(sentences, 1)

    return {
        "text": text,
        "word_count": len(words),
        "sentences": sentences,
        "avg_sentence": round(len(words)/sentences,1),
        "reading_time": round(len(words)/200,1)
    }

def classify_review(n):
    if n < 80: return "Curto"
    elif n < 250: return "Médio"
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

        soup = get_soup(fetch_html(url))
        review = get_review_element(soup)

        if not review:
            st.error("Review não encontrado")
            st.stop()

        usuario = get_username(soup)
        likes = get_likes_given(soup)

        data = analyze_text(review)
        tipo = classify_review(data["word_count"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Palavras", data["word_count"])
        col2.metric("Tempo leitura", data["reading_time"])
        col3.metric("Likes dados", likes)
        col4.metric("Tipo", tipo)

        st.subheader("📋 Estrutura do texto")
        st.write(f"Sentenças: {data['sentences']}")
        st.write(f"Média por frase: {data['avg_sentence']}")

        st.subheader("☁️ Nuvem de palavras")

        top_words = get_top_words(data["text"])
        fig = create_bubble_chart(top_words)

        st.plotly_chart(fig, use_container_width=True)

elif opcao == "Em breve":
    st.title("🚧 Em breve")