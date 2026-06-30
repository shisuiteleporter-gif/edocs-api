"""
Exemplo 4: Criacao de encaminhamento.

Uso:
    EDOCS_CLIENT_ID=seu-id EDOCS_CLIENT_SECRET=seu-secret EDOCS_SCOPE="api-sigades-encaminhamento api-sigades-consultar" python examples/04_encaminhamento.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from edocs_api import EDocsClient, EDocsConfig


def main():
    config = EDocsConfig.from_env()
    if "api-sigades-encaminhamento" not in config.scope:
        print("Aviso: Para este exemplo, inclua api-sigades-encaminhamento no scope")

    client = EDocsClient(config)

    print("=" * 60)
    print("E-Docs API - Encaminhamento")
    print("=" * 60)

    # 1. Obter papel do usuario (remetente)
    print("\n1. Obtendo dados do usuario...")
    papeis = client.consultas.papeis_usuario()
    if not papeis:
        print("  Nenhum papel encontrado.")
        return
    id_papel = papeis[0]["id"]
    print(f"  Papel remetente: [{id_papel}] {papeis[0].get('nome', 'sem nome')}")

    # 2. Buscar um destino (setor)
    print("\n2. Buscando setores para destino...")
    patriarcas = client.agente.listar_patriarcas()
    orgaos = client.agente.listar_organizacoes(patriarcas[0]["id"])
    if not orgaos:
        print("  Nenhum orgao encontrado.")
        return
    setores = client.agente.listar_setores(orgaos[0]["id"])
    if not setores:
        print("  Nenhum setor encontrado. Usando orgao como destino.")
        destino = {"tipo": "Organizacao", "id": orgaos[0]["id"]}
    else:
        destino = {"tipo": "Unidade", "id": setores[0]["id"]}
    print(f"  Destino: {destino}")

    # 3. Criar encaminhamento
    print("\n3. Criando encaminhamento...")
    try:
        id_evento = client.encaminhamentos.novo(
            id_papel_remetente=id_papel,
            destinatarios=[destino],
            assunto="Encaminhamento de teste via API",
            mensagem="Este e um encaminhamento de teste gerado pela API Python do E-Docs.",
            enviar_email=False,
        )
        print(f"  Encaminhamento enviado! idEvento: {id_evento}")

        # 4. Aguardar processamento
        print("\n4. Aguardando processamento...")
        evento = client.aguardar_evento(id_evento)
        print(f"  Evento processado: {evento.get('status')}")
        print(f"  idEncaminhamento: {evento.get('idEncaminhamento', 'N/A')}")

    except Exception as e:
        print(f"  Erro ao criar encaminhamento: {e}")

    print("\nExemplo concluido!")


if __name__ == "__main__":
    main()
