"""Leitura dos dados do dashboard. Tudo é lido uma vez e guardado em cache pelo Streamlit."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
PROCESSADOS = RAIZ / "dados/processados"
DASHBOARD = PROCESSADOS / "dashboard"


def ler_json(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


@st.cache_data
def inct_limpo():
    """Simulação do INCT depois da limpeza: uma linha por nível e bairro."""
    return pd.read_csv(PROCESSADOS / "1_simulacao_inct/inct_longo_limpo.csv")


@st.cache_data
def malha_bairros():
    """Limites oficiais dos 94 bairros (Prefeitura). A propriedade "bairro" corresponde a bairro_malha."""
    return ler_json(RAIZ / "dados/originais/comum/bairros.geojson")


@st.cache_data
def obras():
    """Obras de reconstrução com coordenada e o menor nível em que a água as alcança (vazio se não alcança até 5,4 m)."""
    return pd.read_csv(DASHBOARD / "obras.csv")


@st.cache_data
def mancha(nivel):
    nome = f"{nivel:.1f}".replace(".", "_")
    return ler_json(DASHBOARD / "manchas" / f"nivel_{nome}.geojson")


@st.cache_data
def predios_atingidos_2024():
    return pd.read_csv(DASHBOARD / "p08_poa.csv")


@st.cache_data
def financeiro():
    return ler_json(DASHBOARD / "financeiro.json")
