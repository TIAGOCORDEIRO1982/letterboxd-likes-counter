import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

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
# REVIEW
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


def get_likes_given_elements(soup):
    return soup.select("section.liked-reviews li")


# =========================
# WORD CLOUD
# =========================

def generate_wordcloud(text):
    wc = WordCloud(
        width=800,
        height=400,
        background_color="black"
    ).generate(text)

    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    return fig


# =========================
# EXTRAIR ESTRELAS
# =========================

def extract_star_distribution(liked_elements):
    distribution = {1:0, 2:0, 3:0, 4:0, 5:0}

    for item in liked_elements:
        classes = item.get("class", [])

        for c in classes:
            if "rated-" in c:
                try:
                    rating = int(c.replace("rated-", ""))
                    
                    # converter escala (ex: 80 → 4 estrelas)
                    stars = rating // 20
                    
                    if stars in distribution:
                        distribution[stars] += 1

                except:
                    pass

    return distribution


# =========================
# UI
# =========================

st.title("📊 Letterboxd Analyzer")

url = st.text_input("Cole a URL do Letterboxd:")

if st.button("Analisar"):

    if not url:
        st.warning("Insira uma URL válida")
        st.stop()

    html = fetch_html(url)
    soup = get_soup(html)

    review_element = get_review_element(soup)

    if not review_element:
        st.error("❌ Não foi possível identificar um review nessa página")
        st.stop()

    usuario = get_username(soup)
    liked_elements = get_likes_given_elements(soup)

    # =========================
    # WORD CLOUD
    # =========================

    st.subheader("☁️ Nuvem de palavras")

    text = review_element.get_text()
    fig_wc = generate_wordcloud(text)

    st.pyplot(fig_wc)

    # =========================
    # GRÁFICO DE ESTRELAS
    # =========================

    st.subheader("⭐ Distribuição de avaliações dos likes")

    distribution = extract_star_distribution(liked_elements)

    stars = list(distribution.keys())
    values = list(distribution.values())

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[f"{s}⭐" for s in stars],
        y=values
    ))

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)