# Enchentes em Porto Alegre: dashboard INCT SiMAI

Projeto extensionista da disciplina Coleta, Preparação e Análise de Dados (PUCRS).

**Autor:** João Pedro da Silva Kriger

**Dashboard:** [link público, na versão final]

## Como rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/coleta_bases.py     # baixa as bases externas para dados/originais/
.venv/bin/python scripts/limpeza_inct.py     # gera o JSON do INCT limpo em formato longo
.venv/bin/python scripts/obras_por_nivel.py  # obras dentro da mancha do INCT em cada nível (Tela 2)
.venv/bin/python scripts/cruza_obras_contratos.py  # contrato do TCE-RS por trás do valor das obras de prevenção
.venv/bin/python scripts/prova_testes_inct.py  # gera relatorios/provas_testes_inct.pdf
.venv/bin/python scripts/plota_todos_bairros.py  # curvas por bairro, dados originais e limpos
.venv/bin/python scripts/gera_wireframe.py   # gera relatorios/wireframe_telas.pdf
.venv/bin/python scripts/prepara_dashboard.py  # arquivos leves usados pelo dashboard
.venv/bin/streamlit run app/app.py             # abre o dashboard em http://localhost:8501
```

O arquivo `data.json` do INCT é fornecido pela disciplina e fica em `dados/originais/1_simulacao_inct/`. Os pontos P08 do Copernicus EMSN194 ficam em `dados/originais/comum/copernicus_p08/` e são baixados manualmente, porque o `robots.txt` do site proíbe download automático: o script de coleta indica o link e a pasta.

O notebook de análise exploratória é `notebooks/eda.ipynb`. Os relatórios são compilados com `latexmk -pdf <arquivo>.tex`, dentro de `relatorios/`.

No Streamlit Community Cloud, o app usa o arquivo principal `app/app.py` e as dependências enxutas de `app/requirements.txt`.

Os arquivos do TCE-RS não são versionados, porque contêm CPF e nome de credores pessoa física; `coleta_bases.py --temas tce` os baixa.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `dados/originais/` | dados como vieram da fonte, por tema |
| `dados/processados/` | dados limpos e derivados |
| `app/` | dashboard em Streamlit: Tela 1, Tela 2 e página "Sobre os dados" |
| `scripts/` | coleta, limpeza, preparação dos dados do app, gráficos e wireframe |
| `notebooks/` | análise exploratória e figuras, incluindo as curvas por bairro |
| `relatorios/` | base de dados (Fase 1), limpeza (Fase 2), dashboard (Fase 3), provas dos testes e wireframe |
| `docs/projeto.md` | ideia, decisões, dados e o que eles mostram |

As fontes de cada arquivo estão em `dados/README.md`.
