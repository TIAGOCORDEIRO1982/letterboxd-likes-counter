import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Contador de Likes no Letterboxd")

url = st.text_input("Cole a URL do filme:")

def contar_likes(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "lxml")

    section = soup.select_one("section.liked-reviews")

    if not section:
        return 0

    li_elements = section.select("li")

    return len(li_elements)


if st.button("Contar"):
    if url:
        total = contar_likes(url)
        st.success(f"Total: {total}")
    else:
        st.warning("Cole uma URL")