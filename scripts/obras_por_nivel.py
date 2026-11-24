"""Calcula, para cada nível do Guaíba, as obras de reconstrução que ficam dentro da mancha simulada pelo INCT.

Entradas:
  dados/originais/1_simulacao_inct/mancha_inct_api/map_data_*m.json   manchas do INCT (scripts/coleta_bases.py --temas inct)
  dados/originais/3_investimento_reconstrucao/base_reconstrucao_3_infraestrutura.json
  dados/originais/comum/bairros.geojson
Saída:
  dados/processados/3_investimento_reconstrucao/obras_por_nivel.csv

O valor de cada obra é o investimento PREVISTO pela Prefeitura, não o valor enviado nem o pago.

Uso: python scripts/obras_por_nivel.py
"""
import json
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPolygon, Polygon

warnings.filterwarnings("ignore", category=RuntimeWarning)
RAIZ = Path(__file__).resolve().parent.parent
MANCHAS = RAIZ / "dados/originais/1_simulacao_inct/mancha_inct_api"
OBRAS = RAIZ / "dados/originais/3_investimento_reconstrucao/base_reconstrucao_3_infraestrutura.json"
BAIRROS = RAIZ / "dados/originais/comum/bairros.geojson"
SAIDA = RAIZ / "dados/processados/3_investimento_reconstrucao/obras_por_nivel.csv"
CRS = 31982            # SIRGAS 2000 / UTM 22S, em metros
TOLERANCIA_M = 50      # a coordenada da obra é um ponto; a mancha servida pelo site é simplificada
NIVEIS = [round(3.0 + i / 10, 1) for i in range(25)]  # 3,0 a 5,4 m: faixa realista, até logo acima do recorde de 5,35 m


def carregar_obras():
    with open(OBRAS, encoding="utf-8") as f:
        obras = pd.DataFrame([x["attributes"] for x in json.load(f)["features"]])
    obras["categoria"] = obras["dash"].map({"Sistema de Prevenção": "sistema_protecao", "Infraestrutura": "equipamentos"})
    obras = obras.dropna(subset=["latitude", "longitude"])
    return gpd.GeoDataFrame(obras, geometry=gpd.points_from_xy(obras.longitude, obras.latitude), crs=4326).to_crs(CRS)


def mancha(nivel):
    """Mancha inteira do INCT, sem recorte. Ela não cobre o lago Guaíba (cobre rios e canais menores), e o limite municipal
    simplificado cortaria faixas de orla onde ficam obras, como o Calçadão de Ipanema."""
    with open(MANCHAS / f"map_data_{nivel:.1f}m.json".replace(".", "_", 1), encoding="utf-8") as f:
        feicoes = json.load(f)["flood"]["features"]
    return gpd.GeoDataFrame.from_features(feicoes, crs=4326).to_crs(CRS).make_valid().union_all()


def main():
    uniao = gpd.read_file(BAIRROS).to_crs(CRS).make_valid().union_all()
    # contorno do município, só para medir a área da mancha em Porto Alegre; as frestas da malha simplificada são preenchidas
    municipio = MultiPolygon([Polygon(parte.exterior) for parte in uniao.geoms if isinstance(parte, Polygon)])
    obras = carregar_obras()
    linhas = []
    for nivel in NIVEIS:
        area = mancha(nivel)
        dentro = obras.within(area.buffer(TOLERANCIA_M))
        linha = {"nivel_m": nivel, "area_mancha_km2": round(area.intersection(municipio).area / 1e6, 2),
                 "obras": int(dentro.sum()), "obras_sem_tolerancia": int(obras.within(area).sum()),
                 "previsto_total_mi": round(obras.loc[dentro, "valor_invest"].sum() / 1e6, 2)}
        for categoria in ("sistema_protecao", "equipamentos"):
            sel = dentro & (obras.categoria == categoria)
            linha[f"obras_{categoria}"] = int(sel.sum())
            linha[f"previsto_{categoria}_mi"] = round(obras.loc[sel, "valor_invest"].sum() / 1e6, 2)
        linhas.append(linha)
        print(f"{nivel:.1f} m: {linha['obras']} obras, R$ {linha['previsto_total_mi']:.1f} mi previstos")
    tabela = pd.DataFrame(linhas)
    assert (tabela.area_mancha_km2.diff().dropna() >= -0.05).all(), "a área da mancha diminui com o nível"
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA, index=False)
    print(f"\nobras com localização: {len(obras)} | gerado {SAIDA}")


if __name__ == "__main__":
    main()
