import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(layout="wide")

st.sidebar.title("Menu")
analise = st.sidebar.selectbox(
    "Escolha a análise",
    ["Análise de Like Bait"]
)

st.title("📊 Letterboxd Analytics")

url = st.text_input("Cole a URL do review:")


def extrair_numero(texto):
    match = re.search(r"(\d[\d\.,]*)", texto or "")
    if not match:
        return 0
    return int(match.group(1).replace(".", "").replace(",", ""))


def extrair_dados(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "lxml")

    titulo = soup.select_one("h1.headline-1")
    titulo = titulo.get_text(" ", strip=True) if titulo else "N/A"

    usuario = soup.select_one("a.name")
    usuario = usuario.get_text(" ", strip=True) if usuario else "Usuário"

    review = soup.select_one("div.review")
    review_texto = review.get_text(" ", strip=True) if review else ""

    palavras = len(review_texto.split())
    caracteres = len(review_texto)
    tempo_leitura = round(palavras / 200, 2) if palavras > 0 else 0

    # Likes dados em reviews.
    liked_reviews_section = soup.select_one("section.liked-reviews")
    likes_dados = len(liked_reviews_section.select("li")) if liked_reviews_section else 0

    # Tentativa de capturar likes recebidos da review.
    # Se o HTML não expuser esse número de forma confiável, fica 0.
    review_section = soup.select_one("section.col-12.review.js-review") or soup.select_one("section.review") or soup
    likes_recebidos = 0
    if review_section:
        texto_secao = review_section.get_text(" ", strip=True)
        for padrao in [
            r"(\d[\d\.,]*)\s+likes\b",
            r"(\d[\d\.,]*)\s+like\b",
            r"(\d[\d\.,]*)\s+likes?\s+on\s+this\s+review\b",
        ]:
            m = re.search(padrao, texto_secao, re.IGNORECASE)
            if m:
                likes_recebidos = extrair_numero(m.group(1))
                break

    eficiencia = round((likes_dados / palavras) * 100, 2) if palavras > 0 else 0

    return {
        "titulo": titulo,
        "usuario": usuario,
        "likes_recebidos": likes_recebidos,
        "likes_dados": likes_dados,
        "palavras": palavras,
        "caracteres": caracteres,
        "tempo": tempo_leitura,
        "eficiencia": eficiencia,
    }


if st.button("Analisar"):
    if url:
        dados = extrair_dados(url)

        if not dados:
            st.error("Não foi possível extrair dados. Verifique se a URL é um review válido.")
        else:
            st.subheader(f"🎬 {dados['titulo']}")
            st.caption(f"por {dados['usuario']}")

            st.markdown(f"### 🎯 Like Bait em Reviews dados por **{dados['usuario']}**")

            col1, col2, col3 = st.columns(3)
            col1.metric("Like Review", dados["likes_recebidos"])
            col2.metric("Likes dados em reviews", dados["likes_dados"])
            col3.metric("Tempo de leitura (min)", dados["tempo"])

            st.metric("Eficiência Like Bait (likes dados por 100 palavras)", dados["eficiencia"])

            st.markdown("### 📊 Engajamento")

            df = pd.DataFrame({
                "Tipo": ["Like Review", "Likes dados em reviews"],
                "Quantidade": [dados["likes_recebidos"], dados["likes_dados"]],
            })

            st.bar_chart(df.set_index("Tipo"), use_container_width=True)
    else:
        st.warning("Cole uma URL válida")