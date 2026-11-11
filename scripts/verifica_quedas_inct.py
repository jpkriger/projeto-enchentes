"""Lista os casos em que os prédios afetados de um bairro diminuem quando o nível do Guaíba sobe.

Lê somente o data.json informado, sem nenhuma limpeza, e usa apenas a biblioteca padrão do Python.

Uso:
  python verifica_quedas_inct.py data.json
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

PADRAO = Path(__file__).resolve().parent.parent / "dados/originais/1_simulacao_inct/data.json"


def nivel(chave):
    return float(chave.removesuffix("m").replace("_", "."))


def predios(dados, chave, bairro):
    """Devolve os prédios afetados, ou None se o bairro ou o valor não existir nesse nível."""
    registro = dados[chave].get(bairro)
    valor = registro.get("affected_buildings") if isinstance(registro, dict) else None
    return valor if isinstance(valor, int) else None


def main():
    arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else PADRAO
    if not arquivo.exists():
        sys.exit("Arquivo não encontrado. Uso: python verifica_quedas_inct.py data.json")
    conteudo = arquivo.read_bytes()
    dados = json.loads(conteudo)
    chaves = sorted((chave for chave in dados if re.fullmatch(r"\d+_\dm", chave)), key=nivel)
    bairros = sorted({bairro for chave in chaves for bairro in dados[chave]})

    print(f"Arquivo: {arquivo}")
    print(f"SHA-256: {hashlib.sha256(conteudo).hexdigest()}")
    print(f"Níveis: {len(chaves)} ({nivel(chaves[0])} a {nivel(chaves[-1])} m) | Bairros: {len(bairros)}\n")

    avisos = [f"chave ignorada: {chave}" for chave in dados if chave not in chaves]
    for anterior, atual in zip(chaves, chaves[1:]):
        if round(nivel(atual) - nivel(anterior), 1) != 0.1:
            avisos.append(f"níveis não consecutivos: {anterior} e {atual}")

    quedas = []
    for bairro in bairros:
        for anterior, atual in zip(chaves, chaves[1:]):
            antes = predios(dados, anterior, bairro)
            depois = predios(dados, atual, bairro)
            if antes is None or depois is None:
                avisos.append(f"valor ausente ou inválido: {bairro}, entre {anterior} e {atual}")
            elif depois < antes:
                quedas.append((nivel(atual), bairro, anterior, atual, antes, depois))

    for _, bairro, anterior, atual, antes, depois in sorted(quedas, key=lambda q: (q[1], q[0])):
        print(f'{bairro}: data["{anterior}"] = {antes} prédios -> data["{atual}"] = {depois} prédios ({depois - antes})')

    print(f"\nTotal: {len(quedas)} quedas em {len({q[1] for q in quedas})} bairros")
    for bairro, n in sorted(Counter(q[1] for q in quedas).items()):
        print(f"  {bairro}: {n}")
    if avisos:
        print(f"\nAvisos ({len(avisos)}):")
        for aviso in avisos:
            print(f"  {aviso}")


if __name__ == "__main__":
    main()
