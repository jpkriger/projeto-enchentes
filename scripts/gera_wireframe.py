"""Gera o esboço (wireframe) das telas do dashboard em relatorios/wireframe_telas.pdf.

Uso: python scripts/gera_wireframe.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

SAIDA = Path(__file__).resolve().parent.parent / "relatorios" / "wireframe_telas.pdf"
TINTA = "#2B3A48"
FUNDO = "#EEF2F5"
DESTAQUE = "#DCE8F4"


def caixa(ax, x, y, w, h, texto, cor=FUNDO, tamanho=9, peso="normal"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=cor, edgecolor=TINTA, linewidth=1))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=tamanho, color=TINTA, weight=peso, wrap=True)


def pagina(pdf, titulo, abas, elementos, nota):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(0, 98, titulo, fontsize=14, weight="bold", color=TINTA, va="top")
    x = 0
    for nome, ativa in abas:
        largura = 3 + len(nome) * 0.7
        caixa(ax, x, 86, largura, 5, nome, cor=DESTAQUE if ativa else "white", tamanho=7.5, peso="bold" if ativa else "normal")
        x += largura + 1
    for e in elementos:
        caixa(ax, *e)
    ax.text(0, 1, nota, fontsize=8, color=TINTA, va="bottom")
    pdf.savefig(fig)
    plt.close(fig)


ABAS = ["Tela 1 · Simulação INCT", "Tela 2 · Para onde vai a verba da reconstrução"]


def abas(ativa):
    return [(nome, i == ativa) for i, nome in enumerate(ABAS)]


def main():
    SAIDA.parent.mkdir(exist_ok=True)
    with PdfPages(SAIDA) as pdf:
        pagina(pdf, "Tela 1: se o rio chegar a X metros, quem é afetado?", abas(0), [
            (0, 78, 100, 6, "Aviso visível: estimativas de uma simulação, não previsão nem contagem oficial; acima de 5,35 m, cenários hipotéticos; limitações dos dados", "#FBF1E0", 8),
            (0, 68, 100, 8, "Slider do nível do Guaíba: 3,0 a 10,0 m, passo de 0,1 m (atualiza toda a tela)", DESTAQUE, 10, "bold"),
            (0, 57, 32, 9, "Pessoas afetadas", FUNDO, 10, "bold"), (34, 57, 32, 9, "Prédios afetados", FUNDO, 10, "bold"), (68, 57, 32, 9, "Bairros atingidos", FUNDO, 10, "bold"),
            (0, 6, 49, 48, "Mapa dos bairros colorido pela % de prédios afetados (opcional)"),
            (51, 37, 49, 17, "% de prédios afetados por bairro atingido (barras)"),
            (51, 20, 49, 15, "Curva: população afetada na cidade por nível, com 5,35 m marcado"),
            (51, 6, 49, 12, "Ranking dos bairros mais afetados no nível escolhido"),
        ], "Fonte: somente o JSON do INCT SiMAI, limpo, como pede o enunciado. O recorde de 5,35 m fica entre os níveis simulados de 5,3 e 5,4 m e é marcado na curva.")
        pagina(pdf, "Tela 2: investimento exposto conforme a água avança", abas(1), [
            (0, 74, 48, 9, "Slider do nível: 3,0 a 5,4 m\n(recorde de 5,35 m marcado)", DESTAQUE, 9, "bold"),
            (50, 74, 50, 9, "Filtros: tipo de obra · situação · fonte do recurso", DESTAQUE),
            (0, 61.5, 18.7, 10, "Obras na área\nalcançada", FUNDO, 8.5, "bold"),
            (19.6, 61.5, 18.7, 10, "Investimento exposto\n(previsto nessas obras)", FUNDO, 8.5, "bold"),
            (39.3, 61.5, 18.7, 10, "Equipamentos públicos\nna área alcançada", FUNDO, 8.5, "bold"),
            (0, 8, 58, 51, "Mapa: mancha do INCT no nível escolhido\nobras por tipo (tamanho = valor previsto)\nprédios atingidos em 2024 (Copernicus P08)"),
            (60, 49, 40, 22, "Curva: investimento exposto por nível\n(sistema de proteção × equipamentos)"),
            (60, 27, 40, 20, "Necessidade estimada → solicitado → recebido\n(painel da Prefeitura)"),
            (60, 8, 40, 17, "Ficha da obra: tipo, situação, valor previsto\ne contrato no TCE-RS, quando identificado"),
        ], "Fontes (link e data de coleta no rodapé): INCT SiMAI, Prefeitura (ArcGIS), TCE-RS e Copernicus EMSN194. Exposto = previsto na área alcançada, não custo de dano.")
    print("gerado", SAIDA)


if __name__ == "__main__":
    main()
