"""Monta a pasta entrega_fase2/ só com o que é entregue na Fase 2 (enunciado: scripts de coleta, JSON do INCT
limpo em formato longo, relatorios/limpeza_dados.pdf, notebook de EDA com 6 a 10 gráficos e wireframe das telas).

Rode depois de atualizar relatório, notebook e wireframe: a pasta é apagada e recriada a partir dos arquivos atuais.

Uso: python scripts/monta_entrega.py
"""
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "entrega_fase2"

ARQUIVOS = {
    "1_scripts_coleta/coleta_bases.py": "scripts/coleta_bases.py",
    "2_json_inct_limpo/inct_longo_limpo.json": "dados/processados/1_simulacao_inct/inct_longo_limpo.json",
    "2_json_inct_limpo/inct_longo_limpo.csv": "dados/processados/1_simulacao_inct/inct_longo_limpo.csv",
    "2_json_inct_limpo/inct_alteracoes.csv": "dados/processados/1_simulacao_inct/inct_alteracoes.csv",
    "2_json_inct_limpo/limpeza_inct.py": "scripts/limpeza_inct.py",
    "3_relatorio_limpeza/limpeza_dados.pdf": "relatorios/limpeza_dados.pdf",
    "3_relatorio_limpeza/provas_testes_inct.pdf": "relatorios/provas_testes_inct.pdf",
    "4_notebook_eda/eda.ipynb": "notebooks/eda.ipynb",
    "5_wireframe/wireframe_telas.pdf": "relatorios/wireframe_telas.pdf",
    "6_curvas_por_bairro/plota_todos_bairros.py": "scripts/plota_todos_bairros.py",
}

LEIA_ME = """# Entrega da Fase 2: dados limpos e EDA

Projeto Extensionista de Coleta, Preparação e Análise de Dados (PUCRS). Autor: João Pedro da Silva Kriger.

Esta pasta é uma cópia dos arquivos da entrega, para leitura. Os scripts e o notebook dependem da estrutura completa do
projeto (pastas `dados/`, `scripts/` e `notebooks/`) e não rodam a partir desta pasta. O notebook pode ser lido com todas
as saídas e figuras já embutidas.

1. `1_scripts_coleta/`: script de coleta das bases externas (Prefeitura via ArcGIS, manchas do INCT, TCE-RS e
   instruções do download manual do Copernicus).
2. `2_json_inct_limpo/`: JSON do INCT em formato longo e limpo (também em CSV), o registro de cada valor alterado e o
   script de limpeza.
3. `3_relatorio_limpeza/`: relatório de limpeza e o documento com a prova gráfica dos testes de conteúdo do JSON.
4. `4_notebook_eda/`: notebook de análise exploratória, com os gráficos e comentários da Tela 1 e da Tela 2.
5. `5_wireframe/`: esboço das duas telas do dashboard.
6. `6_curvas_por_bairro/`: script que gera, a partir do `data.json` original, a curva de prédios afetados e a de pessoas
   afetadas por nível do rio em cada bairro, antes e depois da limpeza, e as imagens geradas. Nas imagens `*_original_*.png`
   os pontos vermelhos marcam os níveis em que o número cai; nas `*_limpo_*.png` não há quedas.
"""


def main():
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    for destino, origem in ARQUIVOS.items():
        alvo = DESTINO / destino
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / origem, alvo)
        print(f"  {destino}")
    curvas = DESTINO / "6_curvas_por_bairro"
    for imagem in sorted((RAIZ / "notebooks/figs/curvas_por_bairro").glob("*.png")):
        shutil.copy2(imagem, curvas / imagem.name)
        print(f"  6_curvas_por_bairro/{imagem.name}")
    (DESTINO / "LEIA-ME.md").write_text(LEIA_ME, encoding="utf-8")
    print(f"gerado {DESTINO}")


if __name__ == "__main__":
    main()
