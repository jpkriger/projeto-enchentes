"""Prepara os arquivos leves usados pelo dashboard (app/), para que o app não precise de geopandas.

Entradas: dados limpos do INCT, manchas do INCT, base de obras e painel financeiro da Prefeitura, pontos P08 do Copernicus.
Saídas em dados/processados/dashboard/:
  obras.csv                   uma linha por obra com coordenada, com o menor nível em que a água a alcança
  manchas/nivel_3_0.geojson   mancha do INCT de cada nível (3,0 a 5,4 m), recortada pelo município e simplificada
  p08_poa.csv                 latitude e longitude dos prédios atingidos em 2024 (Copernicus P08) em Porto Alegre
  financeiro.json             necessidade estimada, solicitado, recebido e recursos aplicados

Uso: python scripts/prepara_dashboard.py
"""
import json
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)
RAIZ = Path(__file__).resolve().parent.parent
ORIGINAIS = RAIZ / "dados/originais"
SAIDA = RAIZ / "dados/processados/dashboard"
CRS_METROS = 31982            # SIRGAS 2000 / UTM 22S
TOLERANCIA_M = 50             # mesma tolerância de scripts/obras_por_nivel.py
SIMPLIFICACAO_M = 15          # simplificação do desenho da mancha, só para exibir no mapa
NIVEIS = [round(3.0 + i / 10, 1) for i in range(25)]   # 3,0 a 5,4 m


def nome_do_nivel(nivel):
    """3.0 vira "3_0", como nos nomes de arquivo."""
    return f"{nivel:.1f}".replace(".", "_")


def ler_json(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def municipio():
    bairros = gpd.read_file(ORIGINAIS / "comum/bairros.geojson").to_crs(CRS_METROS)
    return bairros.make_valid().union_all()


def mancha_do_nivel(nivel, limite):
    caminho = ORIGINAIS / f"1_simulacao_inct/mancha_inct_api/map_data_{nome_do_nivel(nivel)}m.json"
    feicoes = ler_json(caminho)["flood"]["features"]
    geometria = gpd.GeoDataFrame.from_features(feicoes, crs=4326).to_crs(CRS_METROS).make_valid().union_all()
    return geometria.intersection(limite)


def preparar_obras(manchas):
    """Uma linha por obra com coordenada; nivel_alcance é o menor nível em que a obra fica a até 50 m da mancha."""
    registros = ler_json(ORIGINAIS / "3_investimento_reconstrucao/base_reconstrucao_3_infraestrutura.json")["features"]
    obras = pd.DataFrame([registro["attributes"] for registro in registros])
    obras = obras.dropna(subset=["latitude", "longitude"]).copy()

    categoria = []
    for grupo in obras["dash"]:
        if grupo == "Sistema de Prevenção":
            categoria.append("Sistema de proteção")
        else:
            categoria.append("Equipamentos públicos")
    obras["categoria"] = categoria
    obras["tipo"] = obras["tema"].fillna("Sistema de proteção")
    obras["situacao"] = obras["obra_status"].fillna("SEM SITUAÇÃO INFORMADA").str.capitalize()

    pontos = gpd.GeoDataFrame(obras, geometry=gpd.points_from_xy(obras.longitude, obras.latitude), crs=4326).to_crs(CRS_METROS)
    nivel_alcance = pd.Series(float("nan"), index=pontos.index)
    for nivel in NIVEIS:
        dentro = pontos.within(manchas[nivel].buffer(TOLERANCIA_M))
        ainda_sem_nivel = nivel_alcance.isna()
        nivel_alcance[dentro & ainda_sem_nivel] = nivel
    obras["nivel_alcance"] = nivel_alcance

    colunas = {"proj_serv": "obra", "categoria": "categoria", "tipo": "tipo", "situacao": "situacao", "bairro": "bairro",
               "valor_invest": "valor_previsto", "latitude": "lat", "longitude": "lon", "nivel_alcance": "nivel_alcance"}
    return obras[list(colunas)].rename(columns=colunas)


def salvar_manchas(manchas):
    pasta = SAIDA / "manchas"
    pasta.mkdir(parents=True, exist_ok=True)
    for nivel, geometria in manchas.items():
        simplificada = geometria.simplify(SIMPLIFICACAO_M)
        gdf = gpd.GeoDataFrame({"nivel_m": [nivel]}, geometry=[simplificada], crs=CRS_METROS).to_crs(4326)
        gdf.to_file(pasta / f"nivel_{nome_do_nivel(nivel)}.geojson", driver="GeoJSON", COORDINATE_PRECISION=5)


def preparar_p08(limite):
    pasta = ORIGINAIS / "comum/copernicus_p08"
    partes = []
    for arquivo in sorted(pasta.glob("*.geojson")):
        partes.append(gpd.read_file(arquivo)[["geometry"]])
    pontos = pd.concat(partes).to_crs(CRS_METROS)
    pontos = pontos[pontos.within(limite)].to_crs(4326)
    return pd.DataFrame({"lat": pontos.geometry.y.round(5), "lon": pontos.geometry.x.round(5)})


def preparar_financeiro():
    recursos = pd.DataFrame([r["attributes"] for r in ler_json(ORIGINAIS / "3_investimento_reconstrucao/hub_base_financeiro_2_recursos.json")["features"]])
    aplicados = pd.DataFrame([r["attributes"] for r in ler_json(ORIGINAIS / "3_investimento_reconstrucao/hub_base_financeiro_1.json")["features"]])

    nomes_curtos = {"equipamentos": "Equipamentos e infraestrutura", "habita": "Habitação", "abastecimento": "Água, esgoto e drenagem",
                    "diques": "Diques e adequação viária", "arrecada": "Perda de arrecadação", "macrodrenagem": "Expansão da macrodrenagem"}
    necessidade = {}
    for _, linha in recursos[recursos["demanda"].notna()].iterrows():
        for chave, nome in nomes_curtos.items():
            if chave in linha["demanda"].lower():
                necessidade[nome] = round(float(linha["valor"]), 2)

    pedidos = {}
    for _, linha in recursos[recursos["recurso"].notna()].iterrows():
        grupo = linha["gráfico"]
        if grupo == "Demais Despesas Emergência":
            grupo = "Emergência"
        pedidos.setdefault(grupo, {})[linha["recurso"]] = round(float(linha["valor"]), 2)

    return {
        "necessidade_estimada": necessidade,
        "solicitado_recebido": pedidos,
        "recursos_aplicados_por_origem": {k: round(float(v), 2) for k, v in aplicados.groupby("fonte_q4")["valor_q4"].sum().items()},
        "recursos_aplicados_por_classe": {k: round(float(v), 2) for k, v in aplicados.groupby("classificacao_q4")["valor_q4"].sum().items()},
        "data_dos_registros": "17/09/2026",
    }


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    limite = municipio()
    manchas = {}
    for nivel in NIVEIS:
        manchas[nivel] = mancha_do_nivel(nivel, limite)

    obras = preparar_obras(manchas)
    obras.to_csv(SAIDA / "obras.csv", index=False)
    salvar_manchas(manchas)
    preparar_p08(limite).to_csv(SAIDA / "p08_poa.csv", index=False)
    with open(SAIDA / "financeiro.json", "w", encoding="utf-8") as arquivo:
        json.dump(preparar_financeiro(), arquivo, ensure_ascii=False, indent=1)

    # Confere com scripts/obras_por_nivel.py: o número de obras alcançadas em cada nível precisa ser o mesmo.
    conferencia = pd.read_csv(RAIZ / "dados/processados/3_investimento_reconstrucao/obras_por_nivel.csv")
    for _, linha in conferencia.iterrows():
        alcancadas = int((obras["nivel_alcance"] <= linha["nivel_m"]).sum())
        assert alcancadas == linha["obras"], f"diferença em {linha['nivel_m']} m: {alcancadas} x {linha['obras']}"
    print(f"obras: {len(obras)} | alcançadas a 5,4 m: {int(obras.nivel_alcance.notna().sum())} | gerado {SAIDA}")


if __name__ == "__main__":
    main()
