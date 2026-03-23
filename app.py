import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(layout="wide")

# SIDEBAR
st.sidebar.title("Menu")
modo = st.sidebar.selectbox(
    "Escolha a análise:",
    ["Análise de Like Bait"]
)

st.title("Letterboxd Analytics")

url = st.text_input("Cole a URL do review:")


def extrair_review(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # TEXTO
    review = soup.find("div", class_="review")
    texto = review.get_text(" ", strip=True) if review else ""

    caracteres = len(texto)
    palavras = len(texto.split())

    # TEMPO LEITURA
    tempo_leitura = round(palavras / 200, 2)

    # LIKES (corrigido)
    like_button = soup.find("a", class_="has-icon icon-like")
    likes = int(like_button.get_text(strip=True)) if like_button else 0

    # COMENTÁRIOS
    comments = soup.find_all("li", class_="comment")
    total_comments = len(comments)

    # LIKES EM AMIGOS (heurística melhor)
    friends = soup.find_all("span", class_="avatar -a24")
    likes_amigos = len(friends)

    return {
        "caracteres": caracteres,
        "palavras": palavras,
        "tempo": tempo_leitura,
        "likes": likes,
        "comentarios": total_comments,
        "likes_amigos": likes_amigos
    }


def gerar_serie_fake(data):
    # simulação leve para visual elegante por dia
    base = data["likes"]

    datas = pd.date_range(end=datetime.today(), periods=30)

    valores = [max(0, int(base * (0.5 + i/60))) for i in range(30)]

    df = pd.DataFrame({
        "data": datas,
        "likes": valores
    })

    df["mes"] = df["data"].dt.strftime("%b")

    return df


def plotar(df):
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("data:T", title="Tempo"),
        y=alt.Y("likes:Q", title="Likes"),
        tooltip=["data", "likes"]
    )

    linha = alt.Chart(df).mark_line(point=True).encode(
        x="data:T",
        y="likes:Q"
    )

    st.altair_chart(chart + linha, use_container_width=True)


if st.button("Analisar"):
    data = extrair_review(url)

    if data["likes"] == 0 and data["comentarios"] == 0:
        st.warning("Possível falha na captura. Verifique a URL.")
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

        st.subheader("📈 Engajamento ao longo do tempo")

        df = gerar_serie_fake(data)
        plotar(df)