"""Procura, no LicitaCon do TCE-RS, o contrato por trás do valor informado pela Prefeitura nas obras de prevenção.

A camada de obras de prevenção traz a empresa vencedora e o valor do contrato. O script busca a empresa entre os
fornecedores (pessoa jurídica) dos contratos da Prefeitura (54900) e do DMAE (54907) e testa se o valor da Prefeitura
é um contrato inteiro ou uma fração exata dele (contrato dividido igualmente entre projetos).

Entradas: dados/originais/3_investimento_reconstrucao/base_reconstrucao_4_prevencao.json
          dados/originais/4_rastreabilidade_recurso/tce_rs/licitacon_contrato_orgao_*.zip  (scripts/coleta_bases.py --temas tce)
Saída:    dados/processados/3_investimento_reconstrucao/obras_contratos_rateio.csv

Uso: python scripts/cruza_obras_contratos.py
"""
import json
import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PREVENCAO = RAIZ / "dados/originais/3_investimento_reconstrucao/base_reconstrucao_4_prevencao.json"
TCE = RAIZ / "dados/originais/4_rastreabilidade_recurso/tce_rs"
SAIDA = RAIZ / "dados/processados/3_investimento_reconstrucao/obras_contratos_rateio.csv"
PALAVRAS_GENERICAS = {"LTDA", "ENGENHARIA", "CONTRATACAO", "VIA", "SMAMUS", "SMAMU", "EIRELI"}
TOLERANCIA_RELATIVA = 0.002   # diferença de centavos por arredondamento da divisão


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9 ]", "", texto)


def ler_tce(arquivo):
    tabelas = []
    for orgao in ("54900", "54907"):
        with zipfile.ZipFile(TCE / f"licitacon_contrato_orgao_{orgao}.zip") as z:
            tabela = pd.read_csv(z.open(arquivo), sep=None, engine="python", encoding="utf-8-sig", dtype=str, on_bad_lines="skip")
        tabelas.append(tabela)
    return pd.concat(tabelas, ignore_index=True)


def main():
    contratos = ler_tce("contrato.csv")
    contratos["valor"] = pd.to_numeric(contratos["VL_CONTRATO"].str.replace(",", ".", regex=False), errors="coerce")
    pessoas = ler_tce("pessoas.csv")
    pessoas = pessoas[pessoas["TP_PESSOA"] != "F"].drop_duplicates("NR_DOCUMENTO")
    pessoas["nome"] = pessoas["NM_PESSOA"].map(normalizar)

    with open(PREVENCAO, encoding="utf-8") as f:
        etapas = pd.DataFrame([x["attributes"] for x in json.load(f)["features"]])
    etapas = etapas.dropna(subset=["emp_vencedora", "valor_contrato"])

    linhas = []
    for (empresa, valor), grupo in etapas.groupby(["emp_vencedora", "valor_contrato"]):
        termo = next((t for t in normalizar(empresa).split() if len(t) > 3 and t not in PALAVRAS_GENERICAS), None)
        documentos = pessoas.loc[pessoas["nome"].str.contains(termo, regex=False), "NR_DOCUMENTO"] if termo else []
        candidatos = contratos[contratos["NR_DOCUMENTO"].isin(list(documentos))].copy()
        candidatos["partes"] = candidatos["valor"] / valor
        exatos = candidatos[(candidatos["partes"].round() >= 1)
                            & ((candidatos["partes"] - candidatos["partes"].round()).abs() / candidatos["partes"] < TOLERANCIA_RELATIVA)]
        base = {"empresa_prefeitura": empresa, "valor_prefeitura": valor, "projetos_prefeitura": grupo["proj_serv"].nunique(),
                "fornecedor_encontrado": len(documentos) > 0}
        if exatos.empty:
            linhas.append({**base, "contrato_tce": None})
        for _, c in exatos.iterrows():
            linhas.append({**base, "contrato_tce": f"{c['NR_CONTRATO']}/{c['ANO_CONTRATO']}", "orgao": c["NM_ORGAO"],
                           "valor_contrato_tce": c["valor"], "partes": int(round(c["partes"])), "objeto": c["DS_OBJETO"]})
    resultado = pd.DataFrame(linhas)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(SAIDA, index=False)
    print(resultado.drop(columns=["objeto"], errors="ignore").to_string(index=False))
    print(f"\ngerado {SAIDA}")


if __name__ == "__main__":
    main()
