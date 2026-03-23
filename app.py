import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Letterboxd Analytics")

modo = st.selectbox(
    "Escolha a análise:",
    ["Análise de Like Bait"]
)

url = st.text_input("Cole a URL do review:")


def extrair_review(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # TEXTO DO REVIEW
    review = soup.find("div", class_="review")
    texto = review.get_text(strip=True) if review else ""

    caracteres = len(texto)
    palavras = len(texto.split())

    # TEMPO DE LEITURA (200 palavras/min)
    tempo_leitura = round(palavras / 200, 2)

    # LIKES
    likes_tag = soup.find("span", class_="likes-count")
    likes = int(likes_tag.text.strip()) if likes_tag else 0

    # COMENTÁRIOS
    comments = soup.find_all("div", class_="comment")
    total_comments = len(comments)

    # AMIGOS (heurística simples)
    friends_likes = soup.find_all("a", class_="name")
    total_friends = len(friends_likes)

    return {
        "texto": texto,
        "caracteres": caracteres,
        "palavras": palavras,
        "tempo_leitura": tempo_leitura,
        "likes": likes,
        "comentarios": total_comments,
        "likes_amigos": total_friends
    }


def gerar_metricas(data):
    eficiencia = 0
    if data["palavras"] > 0:
        eficiencia = data["likes"] / data["palavras"] * 100

    return eficiencia


def plotar(data, eficiencia):
    df = pd.DataFrame({
        "Métrica": ["Likes", "Comentários", "Likes Amigos"],
        "Valor": [data["likes"], data["comentarios"], data["likes_amigos"]]
    })

    fig, ax = plt.subplots()

    ax.bar(df["Métrica"], df["Valor"])

    ax.set_title("Engajamento do Review")

    st.pyplot(fig)


if st.button("Analisar"):
    data = extrair_review(url)

    if not data["texto"]:
        st.error("Não foi possível extrair o review.")
    else:
        eficiencia = gerar_metricas(data)

        st.subheader("📊 Análise de Like Bait")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Likes", data["likes"])
        col2.metric("Comentários", data["comentarios"])
        col3.metric("Caracteres", data["caracteres"])
        col4.metric("Tempo leitura (min)", data["tempo_leitura"])

        st.metric("Eficiência (likes por 100 palavras)", round(eficiencia, 2))

        st.subheader("📈 Engajamento")
        plotar(data, eficiencia)

        st.subheader("📝 Texto do Review")
        st.write(data["texto"][:1000])