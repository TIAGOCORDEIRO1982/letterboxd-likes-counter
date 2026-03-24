import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go

st.set_page_config(layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# =========================
# FETCH (CACHE AQUI SOMENTE)
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
            return el, selector

    return None, None


def get_username(soup):
    user = soup.select_one("a.name")
    return user.get_text().strip() if user else "Desconhecido"


def get_likes_given(soup):
    liked = soup.select("section.liked-reviews li")
    return len(liked)


def get_reading_time(review_element):
    words = len(review_element.get_text().split())
    return round(words / 200, 1)


# =========================
# LIKES (SEPARADO)
# =========================

@st.cache_data
def get_likes_html(url):
    if not url.endswith("/"):
        url += "/"
    likes_url = url + "likes/"
    response = requests.get(likes_url, headers=HEADERS, timeout=10)
    return response.text


def parse_likes(html):
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(" ", strip=True)

    match = re.search(r'(\d+)', text)
    if match:
        value = int(match.group(1))
        if value < 10000:
            return value, "regex"

    users = soup.select("li.poster-container")
    if users:
        return len(users), "count"

    return 0, "fallback"


# =========================
# SCORE
# =========================

def calculate_score(recebidos, dados):
    if dados == 0:
        return 0
    return round(recebidos / dados, 2)


# =========================
# UI
# =========================

st.title("📊 Letterboxd Analytics")

DEBUG = st.sidebar.checkbox("Modo Debug")

url = st.text_input("Cole a URL do Letterboxd:")

if st.button("Analisar"):

    if not url:
        st.warning("Insira uma URL válida")
        st.stop()

    st.info("Carregando página...")

    html = fetch_html(url)
    soup = get_soup(html)

    review_element, selector_used = get_review_element(soup)

    if not review_element:
        st.error("❌ Não foi possível identificar um review nessa página")
        st.stop()

    st.success(f"✅ Review detectado ({selector_used})")

    # =========================
    # DADOS
    # =========================

    likes_html = get_likes_html(url)
    likes_recebidos, metodo = parse_likes(likes_html)

    likes_dados = get_likes_given(soup)
    tempo = get_reading_time(review_element)
    usuario = get_username(soup)
    score = calculate_score(likes_recebidos, likes_dados)

    # =========================
    # DEBUG
    # =========================

    if DEBUG:
        st.sidebar.write("Método likes:", metodo)
        st.sidebar.write("Likes recebidos:", likes_recebidos)

    # =========================
    # MÉTRICAS
    # =========================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Likes recebidos", likes_recebidos)
    col2.metric(f"Likes dados ({usuario})", likes_dados)
    col3.metric("Tempo leitura (min)", tempo)
    col4.metric("Like Bait Score", score)

    # =========================
    # GRÁFICO
    # =========================

    st.subheader("📊 Comparação")

    fig = go.Figure()

    fig.add_trace(go.Bar(x=["Recebidos"], y=[likes_recebidos]))
    fig.add_trace(go.Bar(x=["Dados"], y=[likes_dados]))

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INSIGHT
    # =========================

    st.subheader("🧠 Interpretação")

    if score > 5:
        st.success("🔥 Forte sinal de Like Bait")
    elif score > 1:
        st.info("📈 Engajamento equilibrado")
    else:
        st.warning("⚠️ Baixo retorno de likes")