"""Plota prédios e pessoas afetados por nível do Guaíba em todos os bairros, em duas versões.

Saídas, em notebooks/figs/curvas_por_bairro/ (imagens PNG, como as figuras do notebook):
  predios_original_1.png, predios_original_2.png   prédios afetados, dados originais do INCT (data.json)
  pessoas_original_1.png, pessoas_original_2.png   pessoas afetadas, dados originais
  predios_limpo_1.png, ..., pessoas_limpo_2.png     as mesmas curvas com os dados limpos (inct_longo_limpo.json)

Cada painel é um bairro. Um ponto vermelho marca o nível em que o número ficou menor que no nível anterior,
o que não era esperado, já que com o rio mais alto a água deveria alcançar pelo menos os mesmos prédios.

Uso: python scripts/plota_todos_bairros.py
"""
import json
import textwrap
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MaxNLocator

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados/originais/1_simulacao_inct/data.json"
ENTRADA_LIMPA = RAIZ / "dados/processados/1_simulacao_inct/inct_longo_limpo.json"
PASTA_SAIDA = RAIZ / "notebooks/figs/curvas_por_bairro"

TINTA = "#2B3A48"
CINZA = "#55626F"
AZUL = "#2160A8"
VERMELHO = "#C2362B"
COLUNAS = 6
LINHAS = 5
PAINEIS_POR_PAGINA = COLUNAS * LINHAS


# ---------- leitura dos dados ----------

def nivel_em_metros(chave):
    """Converte a chave do JSON em número: "9_7m" vira 9.7."""
    sem_letra = chave.removesuffix("m")
    com_ponto = sem_letra.replace("_", ".")
    return float(com_ponto)


def carregar_original():
    """Lê o data.json original e devolve uma tabela com uma linha por nível e bairro, sem nenhuma correção."""
    with open(ENTRADA, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)   # dados["9_7m"]["Centro Histórico"] -> valores do bairro nesse nível

    linhas = []
    for chave_nivel in dados:
        bairros_do_nivel = dados[chave_nivel]
        for bairro in bairros_do_nivel:
            valores = bairros_do_nivel[bairro]
            linha = {
                "nivel": nivel_em_metros(chave_nivel),
                "bairro": bairro,
                "predios": valores["affected_buildings"],    # prédios afetados, como vieram do INCT
                "pessoas": valores["affected_population"],   # pessoas afetadas, calculadas pelo INCT
            }
            linhas.append(linha)
    return pd.DataFrame(linhas)


def carregar_limpo():
    """Lê o JSON limpo, que já está em formato longo: uma lista com um registro por nível e bairro."""
    with open(ENTRADA_LIMPA, encoding="utf-8") as arquivo:
        registros = json.load(arquivo)

    linhas = []
    for registro in registros:
        linha = {
            "nivel": registro["nivel_m"],
            "bairro": registro["bairro"],
            "predios": registro["affected_buildings"],     # prédios afetados depois da limpeza
            "pessoas": registro["affected_population"],    # pessoas recalculadas com a porcentagem exata
        }
        linhas.append(linha)
    return pd.DataFrame(linhas)


# ---------- quedas ----------

def marcar_quedas(tabela, coluna):
    """Cria a coluna "queda": True quando o valor é menor que o do nível anterior do mesmo bairro.

    A tabela é ordenada antes por bairro e por nível, para que cada linha venha logo depois
    do nível anterior do mesmo bairro.
    """
    tabela = tabela.sort_values(["bairro", "nivel"]).reset_index(drop=True)

    quedas = []
    bairro_anterior = None
    valor_anterior = None
    for indice in range(len(tabela)):
        bairro = tabela.loc[indice, "bairro"]
        valor = tabela.loc[indice, coluna]

        mesmo_bairro = bairro == bairro_anterior
        if mesmo_bairro and valor < valor_anterior:
            quedas.append(True)
        else:
            quedas.append(False)    # primeiro nível do bairro, ou valor igual ou maior

        bairro_anterior = bairro
        valor_anterior = valor

    tabela["queda"] = quedas
    return tabela


# ---------- desenho ----------

def sem_acento(texto):
    """Usado para ordenar os bairros em ordem alfabética sem que os acentos atrapalhem."""
    decomposto = unicodedata.normalize("NFKD", texto)
    return decomposto.encode("ascii", "ignore").decode().lower()


def formatar_milhar(valor, posicao):
    """Formata os números do eixo com ponto de milhar: 12000 vira 12.000."""
    texto = f"{valor:,.0f}"
    return texto.replace(",", ".")


def desenhar_painel(ax, serie, coluna):
    """Desenha a curva de um bairro e marca em vermelho os níveis com queda."""
    quedas = serie[serie["queda"]]
    ax.plot(serie["nivel"], serie[coluna], color=AZUL, lw=1.3)
    ax.scatter(quedas["nivel"], quedas[coluna], color=VERMELHO, s=20, zorder=3, edgecolor="white", linewidth=.5)
    ax.axvline(5.35, color=CINZA, ls=":", lw=.7)   # recorde de maio de 2024

    titulo = serie["bairro"].iloc[0]
    numero_de_quedas = len(quedas)
    if numero_de_quedas == 1:
        titulo = titulo + " · 1 queda"
    elif numero_de_quedas > 1:
        titulo = titulo + f" · {numero_de_quedas} quedas"
    if numero_de_quedas > 0:
        peso = "bold"
    else:
        peso = "normal"
    ax.set_title(titulo, fontsize=7.6, color=TINTA, weight=peso, pad=3)

    ax.set_xlim(3, 10)
    ax.set_xticks([3, 5, 7, 10])
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_locator(MaxNLocator(3, integer=True))
    ax.yaxis.set_major_formatter(FuncFormatter(formatar_milhar))
    ax.tick_params(labelsize=6.3, colors=CINZA, length=2)
    ax.grid(axis="y", alpha=.25)
    ax.spines[["top", "right"]].set_visible(False)


def textos_da_pagina(coluna, versao):
    """Monta o título e o subtítulo de acordo com a medida (prédios ou pessoas) e a versão dos dados."""
    if coluna == "predios":
        medida = "prédios afetados"
        detalhe = ""
    else:
        medida = "pessoas afetadas"
        if versao == "limpo":
            detalhe = " (recalculadas com a porcentagem exata)"
        else:
            detalhe = " (estimativa do arquivo)"

    if versao == "limpo":
        origem = "dados limpos"
        rodape = "Depois da limpeza, nenhuma curva diminui."
    else:
        origem = "dados originais do INCT"
        rodape = "Cada ponto vermelho é um nível em que o número caiu, o que não era esperado."

    titulo = f"{medida.capitalize()} conforme o Guaíba sobe, por bairro ({origem})"
    subtitulo = (f"Eixo horizontal: nível do rio, de 3 a 10 m. Eixo vertical: {medida}{detalhe}, "
                 f"com escala própria em cada painel. Linha pontilhada: recorde de 5,35 m.\n{rodape}")
    return titulo, subtitulo


def separar_bairros(tabela, coluna):
    """Separa os bairros em atingidos em algum nível e nunca atingidos, em ordem alfabética."""
    todos = list(tabela["bairro"].unique())
    todos.sort(key=sem_acento)

    atingidos = []
    nunca_atingidos = []
    for bairro in todos:
        maior_valor = tabela[tabela["bairro"] == bairro][coluna].max()
        if maior_valor > 0:
            atingidos.append(bairro)
        else:
            nunca_atingidos.append(bairro)
    return atingidos, nunca_atingidos


def gerar_imagens(tabela, coluna, versao):
    """Gera as imagens de uma medida (prédios ou pessoas): 30 bairros por imagem."""
    tabela = marcar_quedas(tabela, coluna)
    atingidos, nunca_atingidos = separar_bairros(tabela, coluna)
    titulo, subtitulo = textos_da_pagina(coluna, versao)

    numero_da_imagem = 0
    for inicio in range(0, len(atingidos), PAINEIS_POR_PAGINA):
        numero_da_imagem = numero_da_imagem + 1
        bairros_da_pagina = atingidos[inicio:inicio + PAINEIS_POR_PAGINA]

        fig, grade = plt.subplots(LINHAS, COLUNAS, figsize=(11.69, 8.27))
        fig.suptitle(titulo, fontsize=13, weight="bold", color=TINTA, x=.02, ha="left", y=.985)
        fig.text(.02, .935, subtitulo, fontsize=8.6, color=CINZA, va="top")
        paineis = grade.ravel()   # transforma a grade 5 x 6 numa lista de 30 painéis

        for posicao in range(len(paineis)):
            ax = paineis[posicao]
            if posicao < len(bairros_da_pagina):
                bairro = bairros_da_pagina[posicao]
                serie = tabela[tabela["bairro"] == bairro]
                desenhar_painel(ax, serie, coluna)
            else:
                ax.axis("off")   # painel sobrando na última página
        fig.tight_layout(rect=(0, 0, 1, .885), h_pad=.9, w_pad=.6)

        ultima_pagina = len(bairros_da_pagina) < PAINEIS_POR_PAGINA
        if ultima_pagina:
            escrever_nunca_atingidos(fig, paineis, len(bairros_da_pagina), nunca_atingidos, coluna)
        arquivo = PASTA_SAIDA / f"{coluna}_{versao}_{numero_da_imagem}.png"
        fig.savefig(arquivo, dpi=150)
        plt.close(fig)
        print("gerado", arquivo)

    imprimir_resumo(tabela, versao, coluna, atingidos, nunca_atingidos)


def escrever_nunca_atingidos(fig, paineis, paineis_usados, nunca_atingidos, coluna):
    """Na última página, escreve a lista de bairros que nunca são atingidos, na primeira linha vazia de painéis."""
    paineis_na_linha_incompleta = paineis_usados % COLUNAS
    if paineis_na_linha_incompleta == 0:
        primeiro_painel_vazio = paineis_usados
    else:
        primeiro_painel_vazio = paineis_usados + (COLUNAS - paineis_na_linha_incompleta)
    topo = paineis[primeiro_painel_vazio].get_position().y1

    if coluna == "predios":
        medida = "prédios"
    else:
        medida = "pessoas"
    fig.text(.02, topo, f"{len(nunca_atingidos)} bairros nunca são atingidos (zero {medida} em todos os níveis)",
             fontsize=9, weight="bold", color=TINTA, va="top")
    lista = ", ".join(nunca_atingidos) + "."
    fig.text(.02, topo - .035, textwrap.fill(lista, 165), fontsize=8, color=CINZA, va="top", linespacing=1.5)


def imprimir_resumo(tabela, versao, coluna, atingidos, nunca_atingidos):
    """Mostra no terminal quantas quedas foram encontradas e em quais bairros."""
    quedas_por_bairro = {}
    for indice in range(len(tabela)):
        if tabela.loc[indice, "queda"]:
            bairro = tabela.loc[indice, "bairro"]
            if bairro not in quedas_por_bairro:
                quedas_por_bairro[bairro] = 0
            quedas_por_bairro[bairro] = quedas_por_bairro[bairro] + 1

    total_de_quedas = sum(quedas_por_bairro.values())
    print(f"{versao} | {coluna}: {len(atingidos)} bairros com gráfico, {len(nunca_atingidos)} nunca atingidos, "
          f"{total_de_quedas} quedas em {len(quedas_por_bairro)} bairros: {quedas_por_bairro}")


def main():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    versoes = [
        ("original", carregar_original()),
        ("limpo", carregar_limpo()),
    ]
    for versao, tabela in versoes:
        assert tabela["bairro"].nunique() == 94, "esperado 94 bairros"
        gerar_imagens(tabela, "predios", versao)
        gerar_imagens(tabela, "pessoas", versao)


if __name__ == "__main__":
    main()
