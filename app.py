import streamlit as st

st.set_page_config(page_title="Letterboxd Analytics", layout="wide")

st.title("Letterboxd Analytics")

modo = st.sidebar.selectbox(
    "Escolha a análise:",
    [
        "Contagem simples",
        "Análise por sessões (activity)"
    ]
)

# -------------------------
# MODO 1
# -------------------------
if modo == "Contagem simples":

    import requests
    from bs4 import BeautifulSoup

    st.header("Contador de Likes")

    url = st.text_input("URL do filme:")

    def contar_likes(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        section = soup.select_one("section.liked-reviews")
        if not section:
            return 0

        return len(section.select("li"))

    if st.button("Contar"):
        total = contar_likes(url)
        st.success(f"Total: {total}")


# -------------------------
# MODO 2 (AVISO)
# -------------------------
elif modo == "Análise por sessões (activity)":

    st.header("Análise de Likes por Sessão")

    st.warning("""
    ⚠️ Esta função não funciona online.

    Motivo:
    A página /activity do Letterboxd carrega via JavaScript
    e exige Selenium (Chrome), que não roda no Streamlit Cloud.

    👉 Para usar essa função:
    rode o app LOCALMENTE no seu computador.
    """)

    st.info("""
    Em breve: versão sem Selenium (mais avançada)
    """)