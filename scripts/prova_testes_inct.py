"""Demonstra com gráficos os testes do data.json original (não usa os dados limpos).

Saída: relatorios/provas_testes_inct.pdf e notebooks/figs/prova_t*.png
Uso: python scripts/prova_testes_inct.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parent.parent
FIGS = RAIZ / "notebooks/figs"
PDF = RAIZ / "relatorios/provas_testes_inct.pdf"
AZUL, LARANJA, VERMELHO, CINZA, VERDE, TINTA = "#2160A8", "#D97A1E", "#C2362B", "#8C96A1", "#2A8C7A", "#2B3A48"
CAMPOS = ["affected_buildings", "total_buildings", "percentage", "population", "affected_population"]
plt.rcParams.update({"figure.figsize": (9.5, 5), "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25, "font.size": 10.5})

n = lambda x: f"{round(x):,}".replace(",", ".")
milhar = FuncFormatter(lambda v, _: n(v))
dec = lambda x, c=1: f"{x:.{c}f}".replace(".", ",")
nivel = lambda k: float(k[:-1].replace("_", "."))

raw = json.load(open(RAIZ / "dados/originais/1_simulacao_inct/data.json", encoding="utf-8"))
df = pd.DataFrame([{"nivel_m": nivel(k), "pos": i, "bairro": b, **v} for k, bs in raw.items() for i, (b, v) in enumerate(bs.items())])
df["exato"] = df.affected_buildings / df.total_buildings * 100
ordem_ref = list(next(iter(raw.values())))

figs = []


def titulo(fig, principal, sub):
    h = fig.get_figheight()
    fig.suptitle(principal, fontsize=13.5, weight="bold", color=TINTA, x=.02, ha="left", y=1 - .08 / h, va="top")
    fig.text(.02, 1 - .42 / h, sub, fontsize=10, color="#55626F", ha="left", va="top")
    fig.tight_layout(rect=(0, 0, 1, 1 - .72 / h))


def fecha(nome, fig, resumo):
    fig.savefig(FIGS / f"prova_{nome}.png", dpi=150, bbox_inches="tight")
    figs.append(fig)
    print(f"[{nome}] {resumo}")


def tabela(ax, linhas, colunas, larguras=None):
    ax.axis("off")
    t = ax.table(cellText=linhas, colLabels=colunas, loc="center", cellLoc="center", colWidths=larguras)
    t.auto_set_font_size(False); t.set_fontsize(11); t.scale(1, 2)
    for (l, _), c in t.get_celld().items():
        c.set_edgecolor("#D5DCE2")
        if l == 0:
            c.set_facecolor("#EEF2F5"); c.set_text_props(weight="bold")


# T1: ordem dos bairros
fora = pd.Series({nivel(k): sum(a != b for a, b in zip(ordem_ref, bs)) for k, bs in raw.items()}).sort_index()
ruins = fora[fora > 0]
fig, ax = plt.subplots()
ax.bar(fora.index, fora.values, width=.08, color=[VERMELHO if v else CINZA for v in fora.values])
pos = (ordem_ref.index("Morro Santana") + 1, list(raw["5_3m"]).index("Morro Santana") + 1)
ax.annotate(f"Nível {dec(ruins.index[0])} m: {int(ruins.iloc[0])} bairros fora do lugar.\nMorro Santana foi da {pos[0]}.ª para a {pos[1]}.ª posição.", (ruins.index[0], ruins.iloc[0]), xytext=(6.2, ruins.iloc[0] * .72), arrowprops=dict(arrowstyle="->", color=TINTA))
ax.set_xlabel("Nível do Guaíba (m)"); ax.set_ylabel("Bairros fora da posição")
titulo(fig, "Só um nível tem os bairros em outra ordem", "Compara a ordem dos bairros em cada nível com a ordem do primeiro nível (3,0 m). Zero significa ordem igual.")
fecha("t1_ordem", fig, f"níveis com ordem diferente: {ruins.to_dict()} | posições {pos}")

# T2: nulos e negativos
nulos = {c: sum(1 for bs in raw.values() for v in bs.values() if v.get(c) is None) for c in CAMPOS}
negativos = {c: int((df[c] < 0).sum()) for c in CAMPOS}
fig, ax = plt.subplots(figsize=(9.5, 4))
tabela(ax, [[c, nulos[c], negativos[c], n(df[c].min()), n(df[c].max())] for c in CAMPOS], ["Campo", "Nulos ou ausentes", "Negativos", "Menor valor", "Maior valor"], [.34, .2, .14, .16, .16])
titulo(fig, "Nenhum valor nulo ou negativo", f"Contagem nos {n(len(df))} registros (71 níveis × 94 bairros).")
fecha("t2_nulos", fig, f"nulos {sum(nulos.values())} | negativos {sum(negativos.values())}")

# T3: constantes
dist = df.groupby("bairro")[["total_buildings", "population"]].nunique()
ex = ["Sarandi", "Farrapos", "Centro Histórico", "Menino Deus", "Lami"]
p = df[df.nivel_m.isin([3.0, 5.3, 10.0])].pivot(index="bairro", columns="nivel_m", values=["total_buildings", "population"])
fig, ax = plt.subplots(figsize=(9.5, 4.4))
tabela(ax, [[b] + [n(p.loc[b, ("total_buildings", k)]) for k in (3.0, 5.3, 10.0)] + [n(p.loc[b, ("population", k)]) for k in (3.0, 5.3, 10.0)] for b in ex],
       ["Bairro (exemplos)", "Prédios\n3,0 m", "Prédios\n5,3 m", "Prédios\n10,0 m", "População\n3,0 m", "População\n5,3 m", "População\n10,0 m"], [.26, .12, .12, .12, .13, .13, .13])
titulo(fig, "O total de prédios e a população não mudam com o nível do rio", f"Nos 71 níveis, {int((dist.total_buildings == 1).sum())} de 94 bairros têm um único total de prédios e {int((dist.population == 1).sum())} de 94 têm uma única população.")
fecha("t3_constantes", fig, f"prédios {int((dist.total_buildings == 1).sum())}/94 | população {int((dist.population == 1).sum())}/94")

# T4: afetados <= total
acima = int((df.affected_buildings > df.total_buildings).sum())
faixas = [(df.exato == 0, "0%"), ((df.exato > 0) & (df.exato <= 25), "até 25%"), ((df.exato > 25) & (df.exato <= 50), "25 a 50%"), ((df.exato > 50) & (df.exato <= 75), "50 a 75%"), ((df.exato > 75) & (df.exato < 100), "75 a 99%"), (df.exato == 100, "100%"), (df.exato > 100, "mais de 100%\n(seria erro)")]
vals = [int(m.sum()) for m, _ in faixas]
fig, ax = plt.subplots()
b = ax.bar([r for _, r in faixas], vals, color=[CINZA] * 6 + [VERMELHO]); ax.bar_label(b, labels=[n(v) for v in vals], padding=2)
ax.yaxis.set_major_formatter(milhar); ax.set_xlabel("Parte dos prédios do bairro que está afetada"); ax.set_ylabel("Registros"); ax.grid(axis="x", visible=False)
titulo(fig, "Nenhum bairro tem mais prédios afetados do que prédios", f"{acima} de {n(len(df))} registros passam de 100%.")
fecha("t4_afetados_total", fig, f"acima {acima} | faixas {vals}")

# T5: percentage
dif = df.percentage - df.exato
diverge = int((dif.abs() > .01).sum()); baixo = int((dif < -.01).sum()); igual = len(df) - diverge
exemplos = [("Cristal", 3.0), ("Floresta", 3.0), ("Belém Novo", 3.0), ("Guarujá", 3.0), ("Anchieta", 3.0), ("Boa Vista do Sul", 3.0)]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.9), width_ratios=[1, 1.5])
b = axes[0].bar(["Igual ao\nvalor exato", "Arredondado\npara cima", "Arredondado\npara baixo"], [igual, diverge - baixo, baixo], color=[CINZA, LARANJA, CINZA]); axes[0].bar_label(b, labels=[n(igual), n(diverge - baixo), n(baixo)], padding=2)
axes[0].yaxis.set_major_formatter(milhar); axes[0].set_ylabel("Registros"); axes[0].grid(axis="x", visible=False); axes[0].set_title("Todos os registros", fontsize=11)
ax = axes[1]
for y, (b_, k) in enumerate(exemplos[::-1]):
    r = df[(df.bairro == b_) & (df.nivel_m == k)].iloc[0]
    ax.plot([r.exato, r.percentage], [y, y], color=CINZA, lw=2, zorder=1)
    ax.scatter(r.exato, y, color=AZUL, s=70, zorder=2, label="valor exato" if y == 0 else None); ax.scatter(r.percentage, y, color=LARANJA, s=70, zorder=2, label="valor no arquivo" if y == 0 else None)
    ax.text(r.percentage + .25, y, f"{dec(r.exato, 2)}% → {int(r.percentage)}%", va="center", fontsize=9.5)
ax.set_yticks(range(len(exemplos)), [b_ for b_, _ in exemplos[::-1]]); ax.set_xlim(0, 17); ax.set_xlabel("Porcentagem de prédios afetados"); ax.legend(frameon=False, loc="upper right"); ax.grid(axis="y", visible=False); ax.set_title("Exemplos a 3,0 m", fontsize=11)
titulo(fig, "A porcentagem do arquivo é sempre arredondada para cima", f"Em {n(diverge)} registros o valor difere do cálculo prédios afetados ÷ total. Nenhum foi arredondado para baixo.")
fecha("t5_percentage", fig, f"divergem {diverge} | para baixo {baixo} | iguais {igual} | dif máx {dif.max():.4f}")

# T6: affected_population
calc_arq = df.population * df.percentage / 100
calc_exato = df.population * df.exato / 100
dif_def = df.affected_population - calc_arq
exc = df.affected_population - calc_exato
por_nivel = exc.groupby(df.nivel_m).sum()
n53 = df[df.nivel_m == 5.3].assign(exc=exc, ex=calc_exato).sort_values("exc", ascending=False).head(6).iloc[::-1]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.9))
y = np.arange(len(n53)); axes[0].barh(y + .2, n53.affected_population, .38, color=LARANJA, label="no arquivo"); axes[0].barh(y - .2, n53.ex, .38, color=AZUL, label="com a porcentagem exata")
axes[0].set_yticks(y, n53.bairro); axes[0].xaxis.set_major_formatter(milhar); axes[0].set_xlabel("Pessoas afetadas a 5,3 m"); axes[0].legend(frameon=False, loc="center right"); axes[0].grid(axis="y", visible=False); axes[0].set_title("Bairros com maior excesso a 5,3 m", fontsize=11)
axes[1].bar(por_nivel.index, por_nivel.values, width=.08, color=LARANJA); axes[1].yaxis.set_major_formatter(milhar); axes[1].set_xlabel("Nível do Guaíba (m)"); axes[1].set_ylabel("Pessoas a mais na cidade"); axes[1].set_title("Excesso total na cidade, por nível", fontsize=11)
titulo(fig, "A população afetada herda o arredondamento para cima", f"O campo segue a fórmula população × percentage ÷ 100 (diferença máxima de {dec(dif_def.max(), 2)} pessoa),\nmas como percentage é arredondada, soma de {n(por_nivel.min())} a {n(por_nivel.max())} pessoas a mais.")
fecha("t6_populacao", fig, f"dif {dif_def.min():.3f}..{dif_def.max():.3f} | excesso {por_nivel.min():.0f}..{por_nivel.max():.0f}")

# T7: quedas de prédios
o = df.sort_values(["bairro", "nivel_m"]).copy()
o["queda"] = o.groupby("bairro").affected_buildings.diff()
o["anterior"] = o.groupby("bairro").affected_buildings.shift()
q = o[o.queda < 0]
janelas = {"Centro Histórico": (9.2, 10.0), "Rubem Berta": (8.3, 9.3), "Lageado": (7.7, 8.5), "Espírito Santo": (3.0, 5.2), "Arquipélago": (3.0, 5.6)}
fig, axes = plt.subplots(2, 3, figsize=(12, 7.2))
for ax, (b_, (a, z)) in zip(axes.ravel(), janelas.items()):
    s = o[(o.bairro == b_) & o.nivel_m.between(a, z)]
    ax.plot(s.nivel_m, s.affected_buildings, color=AZUL, lw=2, marker="o", ms=4)
    qs = s[s.queda < 0]
    ax.scatter(qs.nivel_m, qs.affected_buildings, color=VERMELHO, s=90, zorder=3)
    for r in qs.itertuples():
        if b_ != "Arquipélago" and abs(r.queda) >= 50:
            direita = b_ == "Espírito Santo"
            ax.annotate(f"{n(r.anterior)} → {n(r.affected_buildings)}", (r.nivel_m, r.affected_buildings), textcoords="offset points",
                        xytext=(8, 14) if direita and r.nivel_m < 4 else (-14, 42) if direita else (-6, 12), ha="left" if direita and r.nivel_m < 4 else "right",
                        fontsize=9.5, color=VERMELHO, weight="bold")
    extra = " (variam só 14 prédios)" if b_ == "Arquipélago" else ""
    ax.set_title(f"{b_}: {len(qs)} queda{'s' if len(qs) > 1 else ''}{extra}", fontsize=10.5 if extra else 11.5, weight="bold"); ax.set_xlabel("Nível do Guaíba (m)"); ax.set_ylabel("Prédios afetados"); ax.yaxis.set_major_formatter(milhar)
axes[0, 0].set_ylim(bottom=-150)
aux = axes[1, 2]; aux.axis("off")
aux.text(0, .95, "Como ler", fontsize=11.5, weight="bold", color=TINTA, va="top")
aux.text(0, .82, "A linha mostra os prédios afetados\nconforme o rio sobe. Esperava-se\nque só subisse ou ficasse reta.\n\nCada ponto vermelho é um nível\nem que o número caiu.\n\n" + f"Total: {len(q)} quedas em {q.bairro.nunique()} bairros", fontsize=10.5, color=TINTA, va="top", linespacing=1.4)
titulo(fig, "Em 5 bairros, os prédios afetados diminuem quando o rio sobe", "Níveis em que a contagem diminui em relação ao nível anterior.")
fecha("t7_quedas", fig, f"{len(q)} quedas | {q.bairro.value_counts().to_dict()} | soma {int(q.queda.sum())}")

# T8: população total
tot = df.groupby("nivel_m").affected_population.sum()
d = tot.diff().dropna(); neg = d[d < 0]
k = neg.index[0]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), width_ratios=[1.4, 1])
axes[0].plot(tot.index, tot.values, color=AZUL, lw=2.2); axes[0].scatter([k], [tot[k]], color=VERMELHO, s=70, zorder=3); axes[0].axvspan(9.3, 10, color=CINZA, alpha=.15)
axes[0].text(9.65, tot.min() * 1.4, "ampliado\nao lado", ha="center", fontsize=9, color="#55626F")
axes[0].yaxis.set_major_formatter(milhar); axes[0].set_xlabel("Nível do Guaíba (m)"); axes[0].set_ylabel("Pessoas afetadas na cidade")
z = tot.loc[9.3:10.0]
axes[1].plot(z.index, z.values, color=AZUL, lw=2.2, marker="o"); axes[1].scatter([k], [tot[k]], color=VERMELHO, s=90, zorder=3)
anterior = round(k - .1, 1)
axes[1].annotate(f"{n(tot[anterior])} → {n(tot[k])}\n({n(neg.iloc[0])} pessoas)", (k, tot[k]), textcoords="offset points", xytext=(-8, -38), ha="center", color=VERMELHO, weight="bold", fontsize=10)
axes[1].yaxis.set_major_formatter(milhar); axes[1].set_xlabel("Nível do Guaíba (m)"); axes[1].set_ylim(z.min() - 9000, z.max() + 2000)
titulo(fig, f"A população afetada da cidade cai uma única vez: em {dec(k)} m", "A curva deveria só subir. A queda vem do Centro Histórico, que aparece com zero prédios afetados em 9,7 e 9,8 m.")
fecha("t8_populacao_total", fig, f"quedas {neg.to_dict()} | {tot[anterior]} -> {tot[k]}")

with PdfPages(PDF) as pdf:
    for f in figs:
        pdf.savefig(f)
print("gerado", PDF)
