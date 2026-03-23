import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# MENU LATERAL
st.sidebar.title("Menu")
opcao = st.sidebar.selectbox(
    "Escolha a análise",
    ["Análise de Like Bait"]
)

st.title("📊 Letterboxd Analytics")

url = st.text_input("Cole a URL do review:")

# =========================
# FUNÇÕES DE SCRAPING
# =========================

def get_soup(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "lxml")


def get_like_review(soup):
    # tentativa 1 (mais confiável atualmente)
    el = soup.select_one("a[data-track-action='liked']")
    if el and el.text.strip().isdigit():
        return int(el.text.strip())

    # tentativa 2 (fallback)
    el = soup.select_one(".like-count")
    if el and el.text.strip().isdigit():
        return int(el.text.strip())

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

    likes_review = get_like_review(soup)
    likes_dados = get_likes_dados(soup)
    usuario = get_user(soup)
    texto = get_texto(soup)

    palavras = len(texto.split())
    tempo = round(palavras / 200, 1) if palavras else 0

    # =========================
    # METRICS
    # =========================

    col1, col2, col3 = st.columns(3)

    col1.metric("Like Review", likes_review)
    col2.metric(f"Likes dados em reviews de '{usuario}'", likes_dados)
    col3.metric("Tempo de leitura (min)", tempo)

    # =========================
    # GRÁFICO ESTILO REFERÊNCIA
    # =========================

    st.subheader("📊 Comparação")

    df = pd.DataFrame({
        "Tipo": ["Like Review", "Likes Dados"],
        "Valor": [likes_review, likes_dados]
    })

    fig, ax = plt.subplots()

    ax.bar(
        df["Tipo"],
        df["Valor"]
    )

    ax.set_title("Comparação de Engajamento")
    ax.set_ylabel("Quantidade")

    st.pyplot(fig)