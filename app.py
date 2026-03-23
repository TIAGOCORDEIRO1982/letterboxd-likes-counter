import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# =========================
# MENU LATERAL
# =========================

st.sidebar.title("Menu")
opcao = st.sidebar.selectbox(
    "Escolha a análise",
    ["Análise de Like Bait"]
)

st.title("📊 Letterboxd Analytics")

url = st.text_input("Cole a URL do review:")

# =========================
# SCRAPING
# =========================

def get_soup(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "lxml")


def get_like_review(soup):
    # tentativa 1 (mais comum)
    el = soup.select_one("a[href$='/likes/']")
    if el:
        text = el.text.strip()
        if text.isdigit():
            return int(text)

    # tentativa 2
    el = soup.select_one("[data-track-action='liked']")
    if el:
        text = el.text.strip()
        if text.isdigit():
            return int(text)

    # tentativa 3
    el = soup.select_one(".like-count")
    if el:
        text = el.text.strip()
        if text.isdigit():
            return int(text)

    return 0


def get_likes_dados(soup):
    section = soup.select_one("section.liked-reviews")
    if not section:
        return 0
    return len(section.select("li"))


def get_user(soup):
    el = soup.select_one("a.name")
    return el.text.strip() if el else "Usuário"


def get_texto(soup):
    el = soup.select_one(".review .body-text")
    return el.text.strip() if el else ""


# =========================
# EXECUÇÃO
# =========================

if st.button("Analisar"):

    if not url:
        st.warning("Cole uma URL válida")
        st.stop()

    soup = get_soup(url)

    like_review = get_like_review(soup)
    likes_dados = get_likes_dados(soup)
    usuario = get_user(soup)
    texto = get_texto(soup)

    palavras = len(texto.split())
    tempo = round(palavras / 200, 1) if palavras else 0

    # =========================
    # MÉTRICAS
    # =========================

    col1, col2, col3 = st.columns(3)

    col1.metric("Like Review", like_review)
    col2.metric(f"Likes dados em reviews por '{usuario}'", likes_dados)
    col3.metric("Tempo de leitura (min)", tempo)

    # =========================
    # GRÁFICO (ESTILO LIMPO)
    # =========================

    st.markdown("### 📊 Comparação")

    fig = go.Figure()

    # Azul
    fig.add_trace(go.Bar(
        x=["Like Review"],
        y=[like_review],
        name="Recebidos"
    ))

    # Laranja
    fig.add_trace(go.Bar(
        x=["Likes Dados"],
        y=[likes_dados],
        name="Dados"
    ))

    fig.update_layout(
        barmode='group',
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            y=1.1,
            x=0.5,
            xanchor="center"
        )
    )

    st.plotly_chart(fig, use_container_width=True)