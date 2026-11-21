"""Coleta as bases externas do projeto e grava em dados/originais/.

Regras de coleta responsável (robots.txt verificado):
  - dados.tce.rs.gov.br proíbe /api/ e pede 10 s entre acessos: só URLs diretas de download.
  - vhlab.lad.pucrs.br (API do site do INCT) não tem robots.txt: uma consulta por nível, com pausa de 5 s.
  - riskandrecovery.emergency.copernicus.eu proíbe /download/: os pontos P08 do Copernicus EMSN194 são baixados manualmente.
  - Arquivos que já existem não são baixados de novo (use --forcar para repetir).

Uso:
  python scripts/coleta_bases.py                       # todas as bases
  python scripts/coleta_bases.py --temas arcgis        # só algumas
  python scripts/coleta_bases.py --saida /tmp/teste    # grava em outra pasta
"""
import argparse
import time
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
ARCGIS = "https://gis-smamus.portoalegre.rs.gov.br/server/rest/services"
TCE = "https://dados.tce.rs.gov.br/dados"
INCT = "http://vhlab.lad.pucrs.br:5002/api/map-data"

I = "originais/3_investimento_reconstrucao"
V = "originais/1_simulacao_inct"
C = "originais/comum"
R = "originais/4_rastreabilidade_recurso"

# (arquivo, camada, formato, where, campos, simplificação em graus)
CAMADAS = [
    (f"{C}/bairros.geojson", "A02_SOLO_CRIADO/bairros/FeatureServer/0", "geojson", "1=1", "*", 0.0006),
    (f"{C}/cotas_inunda_5_35_limite_muni.geojson", "Hosted/Cotas_inunda_5_35LimiteMuni/FeatureServer/0", "geojson", "1=1", "fid", 0.0004),
    (f"{I}/base_reconstrucao_4_prevencao.json", "HUB/base_reconstrucao/FeatureServer/4", "json", "1=1", "*", None),
    (f"{I}/base_reconstrucao_2_infraestrutura_centroid.json", "HUB/base_reconstrucao/FeatureServer/2", "json", "1=1", "*", None),
    (f"{I}/base_reconstrucao_3_infraestrutura.json", "HUB/base_reconstrucao/FeatureServer/3", "json", "1=1", "*", None),
    (f"{I}/hub_habitacao_1_demhab.json", "HUB/hub_habitacao_/FeatureServer/1", "json", "1=1", "*", None),
    (f"{I}/hub_base_financeiro_1.json", "HUB/hub_base_financeiro/FeatureServer/1", "json", "1=1", "*", None),
    (f"{I}/hub_base_financeiro_2_recursos.json", "HUB/hub_base_financeiro/FeatureServer/2", "json", "1=1", "*", None),
]

# Licitações, contratos e empenhos da Prefeitura (54900) e do DMAE (54907).
ARQUIVOS_TCE = ["licitacon/contrato/orgao/54900", "licitacon/contrato/orgao/54907", "licitacon/licitacao/orgao/54900",
                "licitacon/licitacao/orgao/54907", "municipal/empenhos/2024/54900", "municipal/empenhos/2025/54900",
                "municipal/empenhos/2024/54907", "municipal/empenhos/2025/54907"]
NIVEIS_INCT = [round(3.0 + i / 10, 1) for i in range(25)]  # 3,0 a 5,4 m: faixa usada no slider da Tela 2
P08 = [f"EMSN194_STD_{aoi}_P082DDA_DamageAssessmentP_v01.geojson" for aoi in ("AOI02", "AOI03", "AOI04")]


class Coletor:
    def __init__(self, base, forcar):
        self.base = Path(base)
        self.forcar = forcar
        self.sessao = requests.Session()
        self.sessao.headers["User-Agent"] = "CPAD-PUCRS-projeto-extensionista"

    def destino(self, relativo):
        caminho = self.base / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if caminho.exists() and not self.forcar:
            print(f"  ok (já existe) {relativo}")
            return None
        return caminho

    def baixar(self, url, relativo, pausa=1, metodo="GET", **kw):
        caminho = self.destino(relativo)
        if caminho is None:
            return False
        with self.sessao.request(metodo, url, stream=True, timeout=900, **kw) as r:
            r.raise_for_status()
            with open(caminho, "wb") as f:
                for parte in r.iter_content(1 << 20):
                    f.write(parte)
        print(f"  baixado {relativo} ({caminho.stat().st_size / 1e6:.1f} MB)")
        time.sleep(pausa)
        return True

    def arcgis(self):
        for relativo, camada, formato, where, campos, offset in CAMADAS:
            params = {"where": where, "outFields": campos, "f": formato, "outSR": 4326}
            if formato == "json":
                params.update(returnGeometry="false")
                del params["outSR"]
            if offset:
                params.update(maxAllowableOffset=offset, geometryPrecision=5)
            self.baixar(f"{ARCGIS}/{camada}/query", relativo, pausa=2, params=params)

    def tce(self):
        for caminho in ARQUIVOS_TCE:
            nome = caminho.replace("/", "_")
            self.baixar(f"{TCE}/{caminho}.csv.zip", f"{R}/tce_rs/{nome}.zip", pausa=10)

    def inct(self):
        """Mancha simulada de cada nível, obtida da mesma API usada pelo site do INCT."""
        for nivel in NIVEIS_INCT:
            corpo = {"neighborhood": "", "street": "", "postal_code": "", "amenity": "", "onlyAffectedAmenities": False,
                     "water_level": nivel, "buffer_distance": 0.0002, "map_style": "OpenStreetMap", "map_position": None}
            nome = f"{nivel:.1f}".replace(".", "_")
            try:
                self.baixar(INCT, f"{V}/mancha_inct_api/map_data_{nome}m.json", pausa=5, metodo="POST", json=corpo)
            except requests.RequestException as erro:
                print(f"  FALHOU {nivel} m: {erro}")

    def copernicus(self):
        pasta = self.base / C / "copernicus_p08"
        faltam = [a for a in P08 if not (pasta / a).exists()]
        if faltam:
            print("  DOWNLOAD MANUAL (robots.txt proíbe /download/): https://riskandrecovery.emergency.copernicus.eu/EMSN194/")
            print(f"  salvar em {pasta}: {', '.join(faltam)}")
        else:
            print("  ok (já existe) pontos P08 do Copernicus")


TEMAS = ["arcgis", "inct", "tce", "copernicus"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--temas", nargs="+", choices=TEMAS, default=TEMAS)
    ap.add_argument("--saida", default=str(RAIZ / "dados"))
    ap.add_argument("--forcar", action="store_true", help="baixa de novo mesmo se o arquivo existir")
    args = ap.parse_args()
    coletor = Coletor(args.saida, args.forcar)
    for tema in args.temas:
        print(f"[{tema}]")
        getattr(coletor, tema)()


if __name__ == "__main__":
    main()
