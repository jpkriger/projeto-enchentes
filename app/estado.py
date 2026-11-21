"""Nível do rio compartilhado entre as telas.

As duas telas usam o mesmo nível: mudar o slider em uma muda o ponto de partida da outra
(consistência e visibilidade do estado). A Tela 2 aceita só até 5,4 m, a faixa que a enchente de 2024 alcançou.
"""
import streamlit as st

NIVEL_INICIAL = 5.3


def nivel_atual():
    if "nivel" not in st.session_state:
        st.session_state["nivel"] = NIVEL_INICIAL
    return st.session_state["nivel"]


def guardar_nivel(chave_do_slider):
    """Chamado quando um slider muda: copia o valor dele para o nível compartilhado."""
    st.session_state["nivel"] = round(st.session_state[chave_do_slider], 1)


def ir_para(valor, chave_do_slider):
    """Atalho dos botões: muda o slider e o nível compartilhado."""
    st.session_state[chave_do_slider] = valor
    st.session_state["nivel"] = valor
