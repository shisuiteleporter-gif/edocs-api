"""
Exemplo 1: Consultas basicas - explorando a estrutura organizacional.

Uso:
    EDOCS_CLIENT_ID=seu-id EDOCS_CLIENT_SECRET=seu-secret python examples/01_consulta_agentes.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from edocs_api import EDocsClient, EDocsConfig


def main():
    config = EDocsConfig.from_env()
    client = EDocsClient(config)

    print("=" * 60)
    print("E-Docs API - Consulta de Agentes")
    print("=" * 60)

    # 1. Listar patriarcas
    print("\n--- Patriarcas ---")
    patriarcas = client.agente.listar_patriarcas()
    for p in patriarcas:
        print(f"  [{p['id']}] {p['nome']}")

    if not patriarcas:
        print("  Nenhum patriarca encontrado.")
        return

    # 2. Listar orgaos do primeiro patriarca
    id_patriarca = patriarcas[0]["id"]
    print(f"\n--- Orgaos do patriarca '{patriarcas[0]['nome']}' ---")
    orgaos = client.agente.listar_organizacoes(id_patriarca)
    for o in orgaos:
        sigla = o.get("sigla", "")
        nome = o.get("nome", "")
        print(f"  [{o['id']}] {sigla} - {nome}")

    if orgaos:
        id_orgao = orgaos[0]["id"]
        print(f"\n--- Setores do orgao '{orgaos[0].get('sigla', orgaos[0]['id'])}' ---")
        setores = client.agente.listar_setores(id_orgao)
        for s in setores:
            print(f"  [{s['id']}] {s.get('nome', 'sem nome')}")

        print(f"\n--- Grupos de Trabalho ---")
        grupos = client.agente.listar_grupos_trabalho(id_orgao)
        for g in grupos:
            print(f"  [{g['id']}] {g.get('nome', 'sem nome')}")

    print("\nConcluido!")


if __name__ == "__main__":
    main()
