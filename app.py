import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# =========================
# MENU
# =========================

st.sidebar.title("Menu")
opcao = st.sidebar.selectbox(
    "Escolha a análise",
    ["Análise de Like Bait"]
)

st.title("📊 Letterboxd Analytics")

url = st.text_input("Cole a URL do review:")

# =========================
# HELPERS
# =========================

def get_soup(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "lxml")


def get_like_review(base_url):
    # garante que a URL termine com /
    if not base_url.endswith("/"):
        base_url += "/"

    likes_url = base_url + "likes/"

    total = 0
    page = 1

    while True:
        page_url = likes_url + f"page/{page}/"
        soup = get_soup(page_url)

        # Busca as linhas da tabela de usuários na página de likes
        users = soup.select("table.person-table tbody tr")
        
        # Fallback caso o layout seja diferente
        if not users:
            users = soup.select(".person-summary")

        # Se não encontrar mais usuários, sai do loop
        if not users:
            break

        total += len(users)
        page += 1

    return total


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

    with st.spinner('Analisando os dados do review...'):
        soup = get_soup(url)

        like_review = get_like_review(url)
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
    # GRÁFICO
    # =========================

    st.markdown("### 📊 Comparação")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Like Review"],
        y=[like_review],
        name="Recebidos",
        marker_color="#3b82f6"
    ))

    fig.add_trace(go.Bar(
        x=["Likes Dados"],
        y=[likes_dados],
        name="Dados",
        marker_color="#f97316"
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