import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import re

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        return BeautifulSoup(response.text, "lxml")
    except Exception as e:
        st.error(f"Erro ao acessar a URL: {e}")
        return None


def get_like_review(soup):
    """
    Busca o total de likes diretamente na página do review.
    Procura pelo link que contém 'likes' no href ou texto.
    """
    # Tenta encontrar pelo seletor de link de contagem que o Letterboxd usa
    el = soup.select_one("a.count.tooltip[href$='/likes/']")
    
    if not el:
        # Busca alternativa em toda a página por links que terminam em /likes/
        for a in soup.find_all("a", href=True):
            if "/likes/" in a['href']:
                el = a
                break

    if el:
        # Extrai apenas os números (remove vírgulas, pontos e textos como 'likes')
        texto_limpo = el.text.replace(",", "").replace(".", "").strip()
        numeros = re.findall(r'\d+', texto_limpo)
        return int(numeros[0]) if numeros else 0
        
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

    if "letterboxd.com" not in url:
        st.error("Por favor, cole uma URL válida do Letterboxd.")
        st.stop()

    with st.spinner('Extraindo dados do Letterboxd...'):
        soup = get_soup(url)
        
        if soup:
            # Pegamos o dado de likes RECEBIDOS pelo review
            like_review = get_like_review(soup)
            
            # Pegamos os dados do autor e texto
            likes_dados = get_likes_dados(soup)
            usuario = get_user(soup)
            texto = get_texto(soup)

            palavras = len(texto.split())
            tempo = round(palavras / 200, 1) if palavras else 0

            # =========================
            # MÉTRICAS
            # =========================

            col1, col2, col3 = st.columns(3)

            col1.metric("Like Review (Recebidos)", like_review)
            col2.metric(f"Likes dados em reviews por '{usuario}'", likes_dados)
            col3.metric("Tempo de leitura (min)", tempo)

            # =========================
            # GRÁFICO
            # =========================

            st.markdown("### 📊 Comparação")

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=["Likes Recebidos"],
                y=[like_review],
                name="No Review",
                marker_color="#3b82f6"
            ))

            fig.add_trace(go.Bar(
                x=["Likes Dados"],
                y=[likes_dados],
                name=f"Por {usuario}",
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
        else:
            st.error("Não foi possível carregar a página. Verifique sua conexão ou a URL.")