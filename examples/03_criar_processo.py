"""
Exemplo 3: Autuacao de processo administrativo.

Uso:
    EDOCS_CLIENT_ID=seu-id EDOCS_CLIENT_SECRET=seu-secret EDOCS_SCOPE="api-sigades-processo api-sigades-consultar" python examples/03_criar_processo.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from edocs_api import EDocsClient, EDocsConfig


def main():
    config = EDocsConfig.from_env()
    if "api-sigades-processo" not in config.scope:
        print("Aviso: Para este exemplo, inclua api-sigades-processo no scope")

    client = EDocsClient(config)

    print("=" * 60)
    print("E-Docs API - Autuacao de Processo")
    print("=" * 60)

    # 1. Obter papel do usuario
    print("\n1. Obtendo papeis do usuario...")
    papeis = client.consultas.papeis_usuario()
    if not papeis:
        print("  Nenhum papel encontrado.")
        return
    id_papel = papeis[0]["id"]
    print(f"  Papel selecionado: [{id_papel}] {papeis[0].get('nome', 'sem nome')}")

    # 2. Obter classe documental para processo
    print("\n2. Buscando classe documental...")
    patriarcas = client.agente.listar_patriarcas()
    planos = client.classificacao.listar_planos_ativos(patriarcas[0]["id"])
    classes = client.classificacao.listar_classes_ativas(planos[0]["id"])
    if not classes:
        print("  Nenhuma classe encontrada.")
        return
    id_classe = classes[0]["id"]
    print(f"  Classe: [{id_classe}] {classes[0].get('nome', 'sem nome')}")

    # 3. Autuar processo
    print("\n3. Autuando processo...")
    try:
        id_evento = client.processos.autuar(
            id_papel_autuador=id_papel,
            id_classe_documental=id_classe,
            resumo="Processo de teste criado via API Python",
            interessados=[
                {"tipo": "Papel", "idPapel": id_papel}
            ],
        )
        print(f"  Processo enviado para autuacao! idEvento: {id_evento}")

        # 4. Aguardar processamento
        print("\n4. Aguardando processamento...")
        evento = client.aguardar_evento(id_evento)
        print(f"  Evento processado: {evento.get('status')}")
        print(f"  idProcesso: {evento.get('idProcesso', 'N/A')}")

    except Exception as e:
        print(f"  Erro ao autuar processo: {e}")
        return

    print("\nExemplo concluido!")


if __name__ == "__main__":
    main()
