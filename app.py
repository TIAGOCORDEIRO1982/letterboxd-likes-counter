import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

st.title("📊 Letterboxd Analytics")

url = st.text_input("Cole a URL do filme (com review):")

def extrair_dados(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # 🎬 Título do filme
    titulo = soup.select_one("h1.headline-1")
    titulo = titulo.text.strip() if titulo else "N/A"

    # 👤 Usuário
    usuario = soup.select_one("a.name")
    usuario = usuario.text.strip() if usuario else "N/A"

    # ✍️ Texto do review
    review = soup.select_one("div.review")
    review_texto = review.get_text(separator=" ").strip() if review else ""

    caracteres = len(review_texto)
    palavras = len(review_texto.split())
    tempo_leitura = round(palavras / 200, 2) if palavras > 0 else 0

    # ❤️ Likes (reviews curtidos)
    section = soup.select_one("section.liked-reviews")
    likes = len(section.select("li")) if section else 0

    # 💬 Comentários (estimativa)
    comentarios = soup.select("div.comment")
    total_comentarios = len(comentarios)

    # 📊 Eficiência
    eficiencia = round(likes / palavras * 100, 2) if palavras > 0 else 0

    return {
        "titulo": titulo,
        "usuario": usuario,
        "likes": likes,
        "comentarios": total_comentarios,
        "caracteres": caracteres,
        "palavras": palavras,
        "tempo": tempo_leitura,
        "eficiencia": eficiencia,
        "review": review_texto[:500]  # preview
    }


if st.button("Analisar"):
    if url:
        dados = extrair_dados(url)

        st.subheader(f"🎬 {dados['titulo']}")
        st.caption(f"por {dados['usuario']}")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Likes", dados["likes"])
        col2.metric("Comentários", dados["comentarios"])
        col3.metric("Palavras", dados["palavras"])
        col4.metric("Tempo leitura (min)", dados["tempo"])

        st.metric("Eficiência (likes por 100 palavras)", dados["eficiencia"])

        st.subheader("📊 Engajamento")

        st.bar_chart({
            "Likes": [dados["likes"]],
            "Comentários": [dados["comentarios"]],
        })

        st.subheader("📝 Preview do review")
        st.write(dados["review"])

    else:
        st.warning("Cole uma URL válida")