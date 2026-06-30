"""
Exemplo 2: Upload de documento e captura.

Uso:
    EDOCS_CLIENT_ID=seu-id EDOCS_CLIENT_SECRET=seu-secret EDOCS_SCOPE="api-sigades-documento api-sigades-consultar" python examples/02_upload_documento.py
"""

import os
import sys
import tempfile
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from edocs_api import EDocsClient, EDocsConfig


def criar_pdf_teste(caminho):
    """Gera um PDF simples para teste."""
    c = canvas.Canvas(caminho)
    c.drawString(100, 750, "Documento de teste - API E-Docs")
    c.drawString(100, 730, "Este e um documento gerado automaticamente.")
    c.save()
    print(f"  PDF de teste criado em: {caminho}")


def main():
    config = EDocsConfig.from_env()
    if "api-sigades-documento" not in config.scope:
        print("Aviso: Para este exemplo, use scope com api-sigades-documento")
        print("Ex: EDOCS_SCOPE='api-sigades-documento api-sigades-consultar'")

    client = EDocsClient(config)

    print("=" * 60)
    print("E-Docs API - Upload e Captura de Documento")
    print("=" * 60)

    # 1. Buscar dados do usuario
    print("\n1. Obtendo dados do usuario e papeis...")
    papeis = client.consultas.papeis_usuario()
    if not papeis:
        print("  Nenhum papel encontrado. (Requer usuario servidor)")
        return
    print(f"  Papeis disponiveis: {len(papeis)}")
    for p in papeis[:3]:
        print(f"    [{p['id']}] {p.get('nome', 'sem nome')}")

    # 2. Buscar classe documental
    print("\n2. Buscando classes documentais...")
    patriarcas = client.agente.listar_patriarcas()
    if not patriarcas:
        print("  Nenhum patriarca encontrado.")
        return
    planos = client.classificacao.listar_planos_ativos(patriarcas[0]["id"])
    if not planos:
        print("  Nenhum plano de classificacao encontrado.")
        return
    classes = client.classificacao.listar_classes_ativas(planos[0]["id"])
    if not classes:
        print("  Nenhuma classe encontrada.")
        return
    id_classe = classes[0]["id"]
    print(f"  Classe selecionada: [{id_classe}] {classes[0].get('nome', 'sem nome')}")

    # 3. Criar PDF e fazer upload
    print("\n3. Criando PDF de teste...")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        caminho_pdf = tmp.name
    try:
        criar_pdf_teste(caminho_pdf)

        print("\n4. Fazendo upload do arquivo para nuvem E-Docs...")
        id_arquivo = client.documentos.upload_arquivo(caminho_pdf)
        print(f"  Arquivo enviado! idArquivo: {id_arquivo}")

        # 5. Capturar documento
        print("\n5. Capturando documento (fase de assinatura)...")
        resultado = client.documentos.enviar_como_servidor(
            id_arquivo=id_arquivo,
            id_papel=papeis[0]["id"],
            id_classe_documental=id_classe,
            resumo="Documento de teste gerado via API Python",
            valor_legal="Original",
            natureza="NatoDigital",
        )
        id_evento = resultado.get("idEvento")
        if id_evento:
            print(f"  Documento enviado para captura! idEvento: {id_evento}")
            print("\n6. Aguardando processamento do evento...")
            try:
                evento = client.aguardar_evento(id_evento)
                print(f"  Evento processado: {evento.get('status')}")
                print(f"  idDocumento: {evento.get('idDocumento', 'N/A')}")
            except TimeoutError:
                print("  Aviso: Evento nao processado dentro do tempo limite.")
                print(f"     Consulte manualmente: GET /v2/eventos/{id_evento}")
        else:
            print(f"  Resposta: {resultado}")
    finally:
        if os.path.exists(caminho_pdf):
            os.unlink(caminho_pdf)
            print(f"\n  Arquivo temporario removido: {caminho_pdf}")

    print("\nExemplo concluido!")


if __name__ == "__main__":
    main()
