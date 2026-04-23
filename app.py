import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.isa-agents.com.ar/info/line_up_mndrn.php?lang=en"


def process_data():
    try:
        response = requests.get(URL, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception:
        return None

    table = soup.find("table")

    if not table:
        return None

    data = []

    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        cols_text = [c.get_text(strip=True) for c in cols]

        if len(cols_text) > 10:
            data.append(cols_text)

    if not data:
        return None

    df = pd.DataFrame(data)

    df_selected = pd.DataFrame({
        "vessel": df[2],
        "ops": df[3],
        "cargo": df[5],
        "quantity": df[6],
        "dest/orig": df[7]
    })

    # filtro Brazil
    df_selected["check"] = df_selected.astype(str).agg(" ".join, axis=1).str.lower()
    df_selected = df_selected[df_selected["check"].str.contains("brazil")]
    df_selected = df_selected.drop(columns=["check"])

    return df_selected


# ===== INTERFACE =====
st.set_page_config(page_title="Navios", layout="wide")

st.title("🚢 Navios com destino/origem Brazil")

if st.button("🔎 Buscar dados"):
    with st.spinner("Coletando dados..."):
        df = process_data()

    if df is None or df.empty:
        st.warning("Nenhum dado encontrado.")
    else:
        st.success("Dados carregados!")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Baixar CSV",
            df.to_csv(index=False),
            "navios.csv"
        )