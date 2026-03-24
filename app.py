import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go

st.set_page_config(layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# =========================
# EXTRAIR REVIEW DO FILM
# =========================

@st.cache_data
def extract_review_from_film(film_url):
    try:
        if not film_url.endswith('/'):
            film_url += '/'

        reviews_url = film_url + "reviews/"

        response = requests.get(reviews_url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        review = soup.select_one('a[href*="/review/"]')

        if review:
            return "https://letterboxd.com" + review["href"]

        return None

    except:
        return None


# =========================
# VALIDAR / NORMALIZAR URL
# =========================

@st.cache_data
def resolve_review_url(url):
    if "/review/" in url:
        return url

    review = extract_review_from_film(url)
    return review


# =========================
# LIKES (ROBUSTO)
# =========================

@st.cache_data
def get_total_likes(review_url):
    try:
        if not review_url.endswith('/'):
            review_url += '/'

        url = review_url + "likes/"

        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return 0

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        patterns = [
            r'(\d+)\s+members',
            r'(\d+)\s+likes',
            r'Liked by\s+(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        # fallback: contar usuários visíveis
        users = soup.select("li.poster-container")
        if users:
            return len(users)

        return 0

    except:
        return 0


# =========================
# LIKES DADOS
# =========================

@st.cache_data
def get_likes_given(review_url):
    try:
        response = requests.get(review_url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        liked_section = soup.select("section.liked-reviews li")

        return len(liked_section)

    except:
        return 0


# =========================
# TEMPO DE LEITURA
# =========================

@st.cache_data
def get_reading_time(review_url):
    try:
        response = requests.get(review_url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        review_text = soup.select_one(".review-body")

        if not review_text:
            return 0

        words = len(review_text.get_text().split())

        return round(words / 200, 1)

    except:
        return 0


# =========================
# USUÁRIO
# =========================

@st.cache_data
def get_username(review_url):
    try:
        response = requests.get(review_url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        user = soup.select_one("a.name")

        if user:
            return user.get_text().strip()

        return "Desconhecido"

    except:
        return "Desconhecido"


# =========================
# SCORE DE LIKE BAIT (NOVO)
# =========================

def calculate_like_bait_score(recebidos, dados):
    if dados == 0:
        return 0

    return round(recebidos / dados, 2)


# =========================
# UI
# =========================

st.sidebar.title("Menu")
opcao = st.sidebar.selectbox(
    "Escolha a análise",
    ["Análise de Like Bait"]
)

st.title("📊 Letterboxd Analytics")

url = st.text_input("Cole a URL (review ou film):")

if st.button("Analisar"):

    if not url:
        st.warning("Insira uma URL válida")
        st.stop()

    # =========================
    # RESOLVER REVIEW
    # =========================

    st.info("Detectando review automaticamente...")

    review_url = resolve_review_url(url)

    if not review_url:
        st.error("Esse conteúdo não possui reviews disponíveis")
        st.stop()

    st.success("Review encontrado")

    # =========================
    # COLETA DE DADOS
    # =========================

    likes_recebidos = get_total_likes(review_url)
    likes_dados = get_likes_given(review_url)
    tempo_leitura = get_reading_time(review_url)
    usuario = get_username(review_url)

    score = calculate_like_bait_score(likes_recebidos, likes_dados)

    # =========================
    # MÉTRICAS
    # =========================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Like Review", likes_recebidos)
    col2.metric(f"Likes dados por {usuario}", likes_dados)
    col3.metric("Tempo de leitura (min)", tempo_leitura)
    col4.metric("Like Bait Score", score)

    # =========================
    # GRÁFICO
    # =========================

    st.subheader("📊 Comparação")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Recebidos"],
        y=[likes_recebidos],
        name="Recebidos"
    ))

    fig.add_trace(go.Bar(
        x=["Dados"],
        y=[likes_dados],
        name="Dados"
    ))

    fig.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INTERPRETAÇÃO (INSIGHT)
    # =========================

    st.subheader("🧠 Interpretação")

    if score > 5:
        st.success("Alto potencial de Like Bait")
    elif score > 1:
        st.info("Engajamento equilibrado")
    else:
        st.warning("Baixo retorno de likes")