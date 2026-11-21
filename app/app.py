"""Dashboard das enchentes em Porto Alegre (INCT SiMAI).

Rodar localmente, a partir da raiz do projeto:
  streamlit run app/app.py
"""
import streamlit as st

import sobre
import tela1
import tela2
from estilo import aplicar_css

st.set_page_config(page_title="Enchentes em Porto Alegre", page_icon="🌊", layout="wide")
aplicar_css()

paginas = st.navigation([
    st.Page(tela1.mostrar, title="Tela 1 · Quem é afetado", url_path="simulacao", default=True),
    st.Page(tela2.mostrar, title="Tela 2 · Investimento exposto", url_path="investimento"),
    st.Page(sobre.mostrar, title="Sobre os dados", url_path="sobre"),
], position="top")
paginas.run()
