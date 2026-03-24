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
    ["Análise de Review", "Em breve"]
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

    return [w for w in text.split() if w not in stopwords and len(w) > 3]


def get_top_words(text, n=12):
    return Counter(clean_text(text)).most_common(n)


# =========================
# BUBBLE CHART
# =========================

def create_bubble_chart(word_counts):

    word_counts = sorted(word_counts, key=lambda x: x[1], reverse=True)

    words = [w for w, _ in word_counts]
    values = [v for _, v in word_counts]

    max_val = max(values)

    sizes = [60 + (v / max_val) * 120 for v in values]
    radii = [s / 2 for s in sizes]

    gap = 12

    x = [0]
    y = [0]

    n = len(words) - 1

    angle_step = 2 * math.pi / n if n > 0 else 0
    base_radius = radii[0] + max(radii[1:], default=0) + gap

    for i in range(1, len(words)):
        angle = (i - 1) * angle_step
        x.append(math.cos(angle) * base_radius)
        y.append(math.sin(angle) * base_radius)

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
        marker=dict(size=sizes, color=colors[:len(words)]),
        textfont=dict(size=13, color="white")
    ))

    fig.update_layout(
        template="plotly_dark",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        height=550
    )

    return fig


# =========================
# ANÁLISE TEXTO
# =========================

def analyze_text(review_element):
    text = review_element.get_text()

    words = text.split()
    word_count = len(words)

    sentences = max(text.count('.') + text.count('!') + text.count('?'), 1)

    return {
        "text": text,
        "word_count": word_count,
        "sentences": sentences,
        "avg_sentence": round(word_count / sentences, 1),
        "reading_time": round(word_count / 200, 1)
    }


def classify_review(word_count):
    if word_count < 80:
        return "Curto"
    elif word_count < 250:
        return "Médio"
    return "Longo"


# =========================
# LIKE BAIT (NOVO)
# =========================

def extract_username_from_url(url):
    try:
        return url.split("letterboxd.com/")[1].split("/")[0]
    except:
        return None


def get_profile_likes(username, max_pages=3):
    total = 0
    recent = 0

    for page in range(1, max_pages + 1):
        url = f"https://letterboxd.com/{username}/likes/page/{page}/"
        html = fetch_html(url)
        soup = get_soup(html)

        items = soup.select("li.poster-container")

        if not items:
            break

        if page == 1:
            recent = len(items)

        total += len(items)

    return total, recent


def calculate_like_bait_score(total_likes, recent_likes):
    A = min(total_likes / 300, 1) * 10
    B = min(recent_likes / 24, 1) * 10
    return round((A + B) / 2, 1)


def classify_score(score):
    if score < 4:
        return "Baixo"
    elif score < 7:
        return "Moderado"
    elif score < 9:
        return "Alto"
    return "Muito Alto"


# =========================
# UI
# =========================

if opcao == "Análise de Review":

    st.title("📊 Letterboxd Review Analyzer")

    url = st.text_input(
        "Cole a URL do Letterboxd:",
        placeholder="Ex: https://letterboxd.com/usuario/film/nome-do-filme/"
    )

    if st.button("Analisar"):

        if not url:
            st.warning("Insira uma URL válida")
            st.stop()

        with st.spinner("Carregando..."):

            soup = get_soup(fetch_html(url))
            review_element = get_review_element(soup)

            if not review_element:
                st.error("Review não encontrado")
                st.stop()

            usuario = get_username(soup)
            likes_dados = get_likes_given(soup)

            analysis = analyze_text(review_element)
            tipo = classify_review(analysis["word_count"])

        # MÉTRICAS
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Palavras", analysis["word_count"])
        col2.metric("Tempo leitura", analysis["reading_time"])
        col3.metric("Likes dados", likes_dados)
        col4.metric("Tipo", tipo)

        # TEXTO
        st.subheader("📋 Estrutura do texto")
        st.write(f"Sentenças: {analysis['sentences']}")
        st.write(f"Média por frase: {analysis['avg_sentence']}")

        # WORD CLOUD
        st.subheader("☁️ Nuvem de palavras")
        fig_wc = create_bubble_chart(get_top_words(analysis["text"]))
        st.plotly_chart(fig_wc, use_container_width=True)

        # =========================
        # LIKE BAIT ANALYSIS
        # =========================

        st.markdown("---")
        st.subheader("🚨 Análise de Engajamento")

        username = extract_username_from_url(url)

        if username:

            with st.spinner("Analisando perfil..."):

                total_likes, recent_likes = get_profile_likes(username)
                score = calculate_like_bait_score(total_likes, recent_likes)
                classificacao = classify_score(score)

            colA, colB, colC = st.columns(3)

            colA.metric("Likes dados (estimado)", total_likes)
            colB.metric("Likes recentes", recent_likes)
            colC.metric("Score", f"{score}/10")

            st.markdown("### 🧠 Interpretação")
            st.write("Alto volume de distribuição de likes")
            st.write("Atividade recente concentrada em interação")

            st.markdown("## 🚨 Veredito")
            st.success(f"Classificação: {classificacao}")


elif opcao == "Em breve":
    st.title("🚧 Em breve")