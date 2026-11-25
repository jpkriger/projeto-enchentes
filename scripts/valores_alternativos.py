"""Mostra quanto o investimento exposto depende do campo de valor escolhido para as obras do DMAE.

A Prefeitura publica, para as obras do DMAE (grupo "Sistema de Prevenção"), mais de um valor:
  valor_invest      camada 3, valor previsto por obra (o que o dashboard usa)
  val_investimento  camada 4, valor por projeto, repetido em cada etapa; ligado à camada 3 pelo campo id
  valor_cont_dmae   camada 3, valor já contratado pelo DMAE
Nos equipamentos públicos só existe valor_invest, que é usado nas três versões.

Também calcula quanto os diques pesam no investimento exposto e quanto do valor exposto do DMAE é de obras que a
Prefeitura classifica como equipamentos de proteção (camada 4, campo classificacao).

Entradas: dados/processados/dashboard/obras.csv (nível de alcance de cada obra) e as camadas 3 e 4 da base da Prefeitura.
Saída:    dados/processados/3_investimento_reconstrucao/valores_alternativos.csv

Uso: python scripts/valores_alternativos.py
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "dados/originais/3_investimento_reconstrucao"
SAIDA = RAIZ / "dados/processados/3_investimento_reconstrucao/valores_alternativos.csv"


def camada(nome):
    with open(BASE / nome, encoding="utf-8") as arquivo:
        return pd.DataFrame([registro["attributes"] for registro in json.load(arquivo)["features"]])


def main():
    obras = camada("base_reconstrucao_3_infraestrutura.json").dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
    alcance = pd.read_csv(RAIZ / "dados/processados/dashboard/obras.csv")
    assert (obras["proj_serv"].values == alcance["obra"].values).all(), "obras.csv fora de ordem: rode scripts/prepara_dashboard.py"
    obras["nivel_alcance"] = alcance["nivel_alcance"].values

    etapas = camada("base_reconstrucao_4_prevencao.json").groupby("id")[["val_investimento", "classificacao"]].first()
    obras = obras.join(etapas, on="id")
    dmae = obras["dash"] == "Sistema de Prevenção"
    # sem par na camada 4 (prédios do DMAE), fica o valor da camada 3, que nesses casos é vazio
    obras["valor_camada4"] = obras["valor_invest"].where(~dmae, obras["val_investimento"].fillna(obras["valor_invest"]))
    obras["valor_contratado"] = obras["valor_invest"].where(~dmae, obras["valor_cont_dmae"])
    diques = dmae & (obras["escopo_prj"] == "DIQUES")
    protecao = dmae & (obras["classificacao"] == "EQUIPAMENTOS DE PROTEÇÃO")

    linhas = []
    for nivel in [round(3.0 + i / 10, 1) for i in range(25)]:
        alcancadas = obras["nivel_alcance"] <= nivel
        exposto = obras.loc[alcancadas, "valor_invest"].sum()
        exposto_dmae = obras.loc[alcancadas & dmae, "valor_invest"].sum()
        linhas.append({
            "nivel_m": nivel,
            "exposto_camada3_mi": round(exposto / 1e6, 1),
            "exposto_camada4_mi": round(obras.loc[alcancadas, "valor_camada4"].sum() / 1e6, 1),
            "exposto_contratado_mi": round(obras.loc[alcancadas, "valor_contratado"].sum() / 1e6, 1),
            "diques_previsto_mi": round(obras.loc[alcancadas & diques, "valor_invest"].sum() / 1e6, 1),
            "diques_contratado_mi": round(obras.loc[alcancadas & diques, "valor_cont_dmae"].sum() / 1e6, 1),
            "diques_pct_do_exposto": round(obras.loc[alcancadas & diques, "valor_invest"].sum() / exposto * 100, 1),
            "protecao_pct_do_exposto_dmae": round(obras.loc[alcancadas & protecao, "valor_invest"].sum() / exposto_dmae * 100, 1),
        })
    tabela = pd.DataFrame(linhas)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA, index=False)
    print(tabela[tabela["nivel_m"].isin([3.0, 4.0, 5.3, 5.4])].to_string(index=False))
    print(f"\ngerado {SAIDA}")


if __name__ == "__main__":
    main()
