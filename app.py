import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(layout="wide")

# 🔹 MENU LATERAL
st.sidebar.title("Menu")
analise = st.sidebar.selectbox(
    "Escolha a análise",
    ["Análise de Like Bait"]
)

st.title("📊 Letterboxd Analytics")

url = st.text_input("Cole a URL do review:")


def extrair_dados(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # 🎬 Título
    titulo = soup.select_one("h1.headline-1")
    titulo = titulo.text.strip() if titulo else "N/A"

    # 👤 Usuário
    usuario = soup.select_one("a.name")
    usuario = usuario.text.strip() if usuario else "Usuário"

    # ✍️ Review
    review = soup.select_one("div.review")
    review_texto = review.get_text(separator=" ").strip() if review else ""

    palavras = len(review_texto.split())
    tempo_leitura = round(palavras / 200, 2) if palavras > 0 else 0

    # ❤️ Likes recebidos
    section = soup.select_one("section.liked-reviews")
    likes_recebidos = len(section.select("li")) if section else 0

    # ⚠️ Placeholder (não disponível no /film/)
    likes_dados = 0

    eficiencia = round(likes_recebidos / palavras * 100, 2) if palavras > 0 else 0

    return {
        "titulo": titulo,
        "usuario": usuario,
        "likes_recebidos": likes_recebidos,
        "likes_dados": likes_dados,
        "palavras": palavras,
        "tempo": tempo_leitura,
        "eficiencia": eficiencia,
    }


if st.button("Analisar"):
    if url:
        dados = extrair_dados(url)

        # 🎬 Header
        st.subheader(f"🎬 {dados['titulo']}")
        st.caption(f"por {dados['usuario']}")

        # 🧠 NOVO TÍTULO
        st.markdown(
            f"### 🎯 Like Bait em Reviews dados por **{dados['usuario']}**"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Likes recebidos", dados["likes_recebidos"])
        col2.metric("Palavras", dados["palavras"])
        col3.metric("Tempo leitura (min)", dados["tempo"])

        st.metric("Eficiência (likes por 100 palavras)", dados["eficiencia"])

        # 📊 GRÁFICO ELEGANTE
        st.markdown("### 📊 Engajamento")

        df = pd.DataFrame({
            "Tipo": ["Likes recebidos", "Likes dados"],
            "Quantidade": [dados["likes_recebidos"], dados["likes_dados"]]
        })

        st.bar_chart(
            df.set_index("Tipo"),
            use_container_width=True
        )

    else:
        st.warning("Cole uma URL válida")