"""Limpa o data.json do INCT SiMAI e gera o formato longo (uma linha por nível e bairro).

Entrada: dados/originais/1_simulacao_inct/data.json
Saídas em dados/processados/1_simulacao_inct/:
  inct_longo_limpo.csv / .json    dados corrigidos, com os valores originais em colunas próprias
  inct_alteracoes.csv             cada valor de prédios afetados alterado, com o valor original e a regra usada

Etapas da limpeza (detalhes e justificativas em relatorios/limpeza_dados.pdf):
  1. trocar zeros isolados e picos isolados por interpolação entre os níveis vizinhos;
  2. trocar o bloco inicial do Espírito Santo pelo primeiro valor plausível;
  3. garantir que os prédios afetados nunca diminuam quando o rio sobe;
  4. recalcular a porcentagem e a população afetada sem o arredondamento para cima do arquivo;
  5. acrescentar o nome do bairro como está na malha oficial da Prefeitura.

Uso: python scripts/limpeza_inct.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados/originais/1_simulacao_inct/data.json"
MALHA = RAIZ / "dados/originais/comum/bairros.geojson"
SAIDA = RAIZ / "dados/processados/1_simulacao_inct"

# Casos encontrados ao inspecionar as séries de cada bairro.
ZEROS_ISOLADOS = {                      # bairro: níveis em que aparece zero entre valores positivos
    "Centro Histórico": [9.7, 9.8],
    "Rubem Berta": [8.8],
    "Lageado": [8.1],
}
PICOS_ISOLADOS = {                      # bairro: níveis com um salto sem relação com os vizinhos
    "Espírito Santo": [4.7],
}
BLOCO_INICIAL = {                       # bairro: níveis com valor impossível e o nível do primeiro valor plausível
    "Espírito Santo": {"niveis": [3.0, 3.1, 3.2, 3.3, 3.4], "usar_valor_de": 3.5},
}
NOMES_MALHA = {                         # nome no INCT: nome na malha oficial da Prefeitura
    "Coronel Aparício Borges": "Aparício Borges",
    "Mont'Serrat": "Montserrat",
}

COLUNAS_SAIDA = ["nivel_m", "bairro", "bairro_malha", "affected_buildings", "total_buildings", "percentage", "population",
                 "affected_population", "affected_buildings_original", "percentage_original",
                 "affected_population_original", "alterado"]


def nivel_em_metros(chave):
    """Converte a chave do JSON em número: "9_7m" vira 9.7."""
    return float(chave.removesuffix("m").replace("_", "."))


def carregar():
    """Lê o data.json e devolve o arquivo bruto e uma tabela com uma linha por nível e bairro."""
    with open(ENTRADA, encoding="utf-8") as f:
        dados = json.load(f)  # dados["9_7m"]["Centro Histórico"] -> valores do bairro nesse nível

    linhas = []
    for chave_nivel, bairros_do_nivel in dados.items():
        for bairro, valores in bairros_do_nivel.items():
            linhas.append({"nivel_m": nivel_em_metros(chave_nivel), "bairro": bairro, **valores})
    return dados, pd.DataFrame(linhas)


def posicao(tabela, bairro, nivel):
    """Índice da linha de um bairro em um nível."""
    return tabela[(tabela["bairro"] == bairro) & (tabela["nivel_m"] == nivel)].index


def registrar(alteracoes, nivel, bairro, antes, depois, regra):
    alteracoes.append({"nivel_m": nivel, "bairro": bairro, "campo": "affected_buildings",
                       "valor_original": int(antes), "valor_corrigido": int(depois), "regra": regra})


def interpolar(tabela, bairro, niveis, alteracoes, regra):
    """Troca os valores dos níveis indicados por uma reta entre os níveis vizinhos válidos."""
    serie = tabela[tabela["bairro"] == bairro].set_index("nivel_m")["affected_buildings"].astype(float)
    original = serie.copy()
    serie.loc[niveis] = np.nan                               # apaga os valores ruins
    serie = serie.interpolate(method="index").round()        # preenche pela reta entre os vizinhos
    for nivel in niveis:
        tabela.loc[posicao(tabela, bairro, nivel), "affected_buildings"] = int(serie.loc[nivel])
        registrar(alteracoes, nivel, bairro, original.loc[nivel], serie.loc[nivel], regra)


def corrigir_bloco_inicial(tabela, alteracoes):
    """Usa o primeiro valor plausível da série nos níveis iniciais impossíveis."""
    for bairro, caso in BLOCO_INICIAL.items():
        valor_plausivel = tabela.loc[posicao(tabela, bairro, caso["usar_valor_de"]), "affected_buildings"].iloc[0]
        for nivel in caso["niveis"]:
            linha = posicao(tabela, bairro, nivel)
            registrar(alteracoes, nivel, bairro, tabela.loc[linha, "affected_buildings"].iloc[0], valor_plausivel,
                      "bloco inicial incompatível: primeiro valor plausível")
            tabela.loc[linha, "affected_buildings"] = valor_plausivel


def garantir_que_nunca_diminui(tabela, alteracoes):
    """Com o rio mais alto, a contagem não deveria cair: cada nível recebe o maior valor visto até ali no bairro."""
    tabela = tabela.sort_values(["bairro", "nivel_m"]).reset_index(drop=True)
    maior_ate_aqui = tabela.groupby("bairro")["affected_buildings"].cummax()
    for i in tabela.index[tabela["affected_buildings"] != maior_ate_aqui]:
        registrar(alteracoes, tabela.at[i, "nivel_m"], tabela.at[i, "bairro"], tabela.at[i, "affected_buildings"],
                  maior_ate_aqui[i], "monotonia: máximo acumulado")
    tabela["affected_buildings"] = maior_ate_aqui.astype(int)
    return tabela


def recalcular_campos_derivados(tabela):
    """Refaz porcentagem e população a partir dos prédios, sem arredondar para cima no meio da conta."""
    tabela["percentage"] = (tabela["affected_buildings"] / tabela["total_buildings"] * 100).round(2)
    tabela["affected_population"] = (tabela["population"] * tabela["affected_buildings"]
                                     / tabela["total_buildings"]).round().astype(int)


def limpar(tabela):
    alteracoes = []
    tabela = tabela.sort_values(["nivel_m", "bairro"]).reset_index(drop=True)  # acesso sempre por nome, não por posição

    # Guarda os valores do arquivo antes de qualquer mudança.
    tabela = tabela.rename(columns={"percentage": "percentage_original",
                                    "affected_population": "affected_population_original"})
    tabela["affected_buildings_original"] = tabela["affected_buildings"]

    # 1. Zeros e picos isolados.
    for bairro, niveis in ZEROS_ISOLADOS.items():
        interpolar(tabela, bairro, niveis, alteracoes, "zero isolado: interpolação linear")
    for bairro, niveis in PICOS_ISOLADOS.items():
        interpolar(tabela, bairro, niveis, alteracoes, "pico isolado: interpolação linear")

    # 2. Bloco inicial do Espírito Santo.
    corrigir_bloco_inicial(tabela, alteracoes)

    # 3. Prédios afetados nunca diminuem quando o rio sobe.
    tabela = garantir_que_nunca_diminui(tabela, alteracoes)

    # 4. Porcentagem e população recalculadas.
    recalcular_campos_derivados(tabela)
    tabela["alterado"] = tabela["affected_buildings"] != tabela["affected_buildings_original"]

    # 5. Nome do bairro na malha oficial (o nome do INCT continua em "bairro").
    tabela["bairro_malha"] = tabela["bairro"].replace(NOMES_MALHA)

    tabela = tabela[COLUNAS_SAIDA].sort_values(["nivel_m", "bairro"]).reset_index(drop=True)
    alteracoes = pd.DataFrame(alteracoes).sort_values(["bairro", "nivel_m", "regra"]).reset_index(drop=True)
    return tabela, alteracoes


def validar(tabela):
    """Confere as regras que o dado limpo precisa cumprir. Se alguma falhar, o script para com a mensagem."""
    assert len(tabela) == 71 * 94, "esperado 71 níveis x 94 bairros"
    assert tabela.groupby("nivel_m")["bairro"].nunique().eq(94).all(), "nível sem os 94 bairros"
    assert (tabela.groupby("bairro")["affected_buildings"].diff().dropna() >= 0).all(), "prédios afetados caem com o nível"
    assert tabela["percentage"].between(0, 100).all(), "porcentagem fora de 0 a 100"
    assert (tabela["affected_buildings"] <= tabela["total_buildings"]).all(), "mais prédios afetados que o total"
    assert (tabela.groupby("nivel_m")["affected_population"].sum().diff().dropna() >= 0).all(), "curva de população cai"
    with open(MALHA, encoding="utf-8") as f:
        oficiais = {feicao["properties"]["bairro"] for feicao in json.load(f)["features"]}
    assert set(tabela["bairro_malha"]) == oficiais, "bairro sem correspondência na malha oficial"


def resumo(dados, limpo, alteracoes):
    """Imprime os números citados no relatório."""
    print(f"linhas: {len(limpo)} | níveis: {limpo.nivel_m.nunique()} | bairros: {limpo.bairro.nunique()}")
    print("\nalterações em prédios afetados, por regra:")
    print(alteracoes.groupby("regra").agg(valores=("bairro", "size"), bairros=("bairro", "nunique")).to_string())

    ordem_padrao = list(next(iter(dados.values())))
    print("\nníveis com ordem de bairros diferente:", [chave for chave, bairros in dados.items() if list(bairros) != ordem_padrao])

    exato = limpo.affected_buildings_original / limpo.total_buildings * 100
    print("porcentagem diferente do valor exato (> 0,01):", int(((limpo.percentage_original - exato).abs() > 0.01).sum()))
    print("porcentagem igual ao valor exato arredondado para cima:",
          int((limpo.percentage_original == np.ceil(exato - 1e-9)).sum()), "de", len(limpo))

    totais = limpo.groupby("nivel_m")[["affected_population_original", "affected_population",
                                       "affected_buildings_original", "affected_buildings"]].sum()
    print("\ntotais da cidade (original x limpo):")
    print(totais.loc[[3.0, 4.7, 5.3, 9.6, 9.7, 9.8, 10.0]].to_string())

    # Efeito só do arredondamento: população do arquivo menos a conta exata com os prédios originais.
    exata = limpo.population * limpo.affected_buildings_original / limpo.total_buildings
    excesso = (limpo.affected_population_original - exata).groupby(limpo.nivel_m).sum()
    milhar = lambda v: f"{v:,.0f}".replace(",", ".")
    print(f"\nexcesso de população causado pelo arredondamento: de {milhar(excesso.min())} a {milhar(excesso.max())} pessoas, conforme o nível")
    print("bairros nunca atingidos:", int((limpo.groupby("bairro").affected_buildings.max() == 0).sum()))


def main():
    dados, tabela = carregar()
    limpo, alteracoes = limpar(tabela)
    validar(limpo)

    SAIDA.mkdir(parents=True, exist_ok=True)
    limpo.to_csv(SAIDA / "inct_longo_limpo.csv", index=False)
    limpo.to_json(SAIDA / "inct_longo_limpo.json", orient="records", force_ascii=False, indent=0)
    alteracoes.to_csv(SAIDA / "inct_alteracoes.csv", index=False)
    resumo(dados, limpo, alteracoes)


if __name__ == "__main__":
    main()
