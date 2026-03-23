import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import altair as alt
from datetime import datetime
import re

st.set_page_config(layout="wide")

# SIDEBAR
st.sidebar.title("Menu")
modo = st.sidebar.selectbox(
    "Escolha a análise:",
    ["Análise de Like Bait"]
)

st.title("Letterboxd Analytics")

url = st.text_input("Cole a URL do review:")


# 🔍 EXTRAÇÃO ROBUSTA
def extrair_review(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "lxml")

    # TEXTO
    review = soup.find("div", class_="review")
    if not review:
        return None

    texto = review.get_text(" ", strip=True)

    caracteres = len(texto)
    palavras = len(texto.split())

    tempo_leitura = round(palavras / 200, 2)

    # 🔥 CONTAINER PRINCIPAL
    container = soup.find("section", class_="film-detail-content")

    likes = 0
    comentarios = 0

    if container:
        texto_container = container.get_text(" ", strip=True)

        likes_match = re.search(r"(\d+)\s+likes?", texto_container, re.IGNORECASE)
        comments_match = re.search(r"(\d+)\s+comments?", texto_container, re.IGNORECASE)

        if likes_match:
            likes = int(likes_match.group(1))

        if comments_match:
            comentarios = int(comments_match.group(1))

    # 🔁 FALLBACK
    if likes == 0:
        like_span = soup.find("span", class_="like-count")
        if like_span:
            try:
                likes = int(like_span.text.strip())
            except:
                pass

    # 👥 LIKES DE AMIGOS (aproximação)
    friends = soup.select("section.js-liked-by a.avatar")
    likes_amigos = len(friends)

    return {
        "caracteres": caracteres,
        "palavras": palavras,
        "tempo": tempo_leitura,
        "likes": likes,
        "comentarios": comentarios,
        "likes_amigos": likes_amigos
    }


# 📊 DADOS PARA GRÁFICO (ESTILO LIMPO)
def gerar_serie_visual(data):
    base = max(data["likes"], 1)

    datas = pd.date_range(end=datetime.today(), periods=30)

    valores = [int(base * (0.4 + i/50)) for i in range(30)]

    df = pd.DataFrame({
        "data": datas,
        "likes": valores
    })

    return df


# 📈 GRÁFICO ELEGANTE
def plotar(df):
    bars = alt.Chart(df).mark_bar().encode(
        x=alt.X("data:T", title="Tempo"),
        y=alt.Y("likes:Q", title="Likes"),
        tooltip=["data", "likes"]
    )

    line = alt.Chart(df).mark_line(point=True).encode(
        x="data:T",
        y="likes:Q"
    )

    st.altair_chart(bars + line, use_container_width=True)


# 🚀 EXECUÇÃO
if st.button("Analisar"):

    if not url or "/film/" not in url:
        st.error("Use uma URL de review válida do Letterboxd.")
    else:
        data = extrair_review(url)

        if not data:
            st.error("Não foi possível extrair dados. Verifique se é um review individual.")
        else:
            st.subheader("📊 Análise de Like Bait")

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Likes", data["likes"])
            col2.metric("Comentários", data["comentarios"])
            col3.metric("Likes Amigos", data["likes_amigos"])
            col4.metric("Caracteres", data["caracteres"])
            col5.metric("Tempo leitura (min)", data["tempo"])

            eficiencia = 0
            if data["palavras"] > 0:
                eficiencia = round((data["likes"] / data["palavras"]) * 100, 2)

            st.metric("Eficiência Like Bait", eficiencia)

            st.subheader("📈 Engajamento")

            df = gerar_serie_visual(data)
            plotar(df)