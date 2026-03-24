import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# =========================
# EXTRAIR REVIEW SE FOR FILM
# =========================

@st.cache_data
def extract_review_url(film_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(film_url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        review_link = soup.select_one('a[href*="/review/"]')

        if review_link:
            return "https://letterboxd.com" + review_link["href"]

        return None
    except:
        return None


# =========================
# LIKES (ROBUSTO)
# =========================

@st.cache_data
def get_total_likes(review_url):
    try:
        if not review_url.endswith('/'):
            review_url += '/'

        url = review_url + "likes/"

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

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

        # fallback: contar usuários
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
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(review_url, headers=headers, timeout=10)

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
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(review_url, headers=headers, timeout=10)

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
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(review_url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        user = soup.select_one("a.name")

        if user:
            return user.get_text().strip()

        return "Desconhecido"

    except:
        return "Desconhecido"


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
    # GARANTIR QUE É REVIEW
    # =========================

    if "/review/" not in url:
        st.info("Detectando review automaticamente...")

        new_url = extract_review_url(url)

        if new_url:
            url = new_url
            st.success("Review encontrado automaticamente")
        else:
            st.error("Nenhum review encontrado nessa página")
            st.stop()

    # =========================
    # COLETA DE DADOS
    # =========================

    likes_recebidos = get_total_likes(url)
    likes_dados = get_likes_given(url)
    tempo_leitura = get_reading_time(url)
    usuario = get_username(url)

    # =========================
    # MÉTRICAS
    # =========================

    col1, col2, col3 = st.columns(3)

    col1.metric("Like Review", likes_recebidos)
    col2.metric(f"Likes dados por {usuario}", likes_dados)
    col3.metric("Tempo de leitura (min)", tempo_leitura)

    # =========================
    # GRÁFICO
    # =========================

    st.subheader("📊 Comparação")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Review"],
        y=[likes_recebidos],
        name="Recebidos"
    ))

    fig.add_trace(go.Bar(
        x=["Review"],
        y=[likes_dados],
        name="Dados"
    ))

    fig.update_layout(
        barmode='group',
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)