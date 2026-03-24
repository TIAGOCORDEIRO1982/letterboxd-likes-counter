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
    "User-Agent": "Mozilla/5.0"
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
    for s in [".review-body", ".body-text", ".review"]:
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
# CLUSTER SEMÂNTICO SIMPLES
# =========================

def classify_word_group(word):

    cinema = {"filme","cinema","diretor","ator","roteiro"}
    tempo = {"tempo","memoria","historia","passado","momento"}
    opiniao = {"acho","parece","sinto","gosto","melhor"}
    
    if word in cinema:
        return "cinema"
    elif word in tempo:
        return "tempo"
    elif word in opiniao:
        return "opiniao"
    else:
        return "outro"

def get_color(group):
    palette = {
        "cinema": "#60A5FA",
        "tempo": "#34D399",
        "opiniao": "#FBBF24",
        "outro": "#A78BFA"
    }
    return palette.get(group, "#A78BFA")

# =========================
# FORCE LAYOUT + ANIMAÇÃO
# =========================

def create_bubble_chart(word_counts):

    word_counts = sorted(word_counts, key=lambda x: x[1], reverse=True)

    words = [w for w, _ in word_counts]
    values = [v for _, v in word_counts]

    max_val = max(values)

    sizes = [60 + (v / max_val) * 120 for v in values]
    radii = [s / 2 for s in sizes]

    n = len(words)

    x = [random.uniform(-0.1, 0.1) for _ in range(n)]
    y = [random.uniform(-0.1, 0.1) for _ in range(n)]

    gap = 6

    frames = []

    for step in range(60):

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

        # atração ao centro
        for i in range(1, n):
            x[i] += (-x[i]) * 0.05
            y[i] += (-y[i]) * 0.05

        x[0], y[0] = 0, 0  # fixa maior

        frames.append(go.Frame(data=[go.Scatter(
            x=x,
            y=y
        )]))

    labels = [f"{w}<br>{v}x" for w, v in word_counts]

    colors = [get_color(classify_word_group(w)) for w in words]

    fig = go.Figure(
        data=[go.Scatter(
            x=x,
            y=y,
            mode='markers+text',
            text=labels,
            textposition="middle center",
            marker=dict(size=sizes, color=colors),
            textfont=dict(color="white")
        )],
        frames=frames
    )

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