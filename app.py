# =========================
# NOVAS FUNÇÕES (ADICIONADAS)
# =========================

def extract_username_from_url(url):
    try:
        return url.split("letterboxd.com/")[1].split("/")[0]
    except:
        return None


def get_profile_likes(username, max_pages=3):
    total = 0
    recent = 0

    for page in range(1, max_pages + 1):
        url = f"https://letterboxd.com/{username}/likes/page/{page}/"
        html = fetch_html(url)
        soup = get_soup(html)

        items = soup.select("li.poster-container")

        if not items:
            break

        if page == 1:
            recent = len(items)

        total += len(items)

    return total, recent


def calculate_like_bait_score(total_likes, recent_likes):

    # intensidade total
    A = min(total_likes / 300, 1) * 10

    # intensidade recente
    B = min(recent_likes / 24, 1) * 10

    # combinação simples
    score = (A + B) / 2

    return round(score, 1)


def classify_score(score):
    if score < 4:
        return "Baixo"
    elif score < 7:
        return "Moderado"
    elif score < 9:
        return "Alto"
    return "Muito Alto"


# =========================
# INTEGRAÇÃO NA UI
# =========================

        # =========================
        # LIKE BAIT ANALYSIS (NOVO)
        # =========================

        st.markdown("---")
        st.subheader("🚨 Análise de Engajamento")

        username = extract_username_from_url(url)

        if username:

            with st.spinner("Analisando comportamento do perfil..."):

                total_likes, recent_likes = get_profile_likes(username)

                score = calculate_like_bait_score(total_likes, recent_likes)
                classificacao = classify_score(score)

            colA, colB, colC = st.columns(3)

            colA.metric("Likes dados (estimado)", total_likes)
            colB.metric("Likes recentes", recent_likes)
            colC.metric("Score", f"{score}/10")

            st.markdown("### 🧠 Interpretação")

            st.write("Alto volume de distribuição de likes")
            st.write("Atividade recente concentrada em interação")

            st.markdown("## 🚨 Veredito")

            st.success(f"Classificação: {classificacao}")