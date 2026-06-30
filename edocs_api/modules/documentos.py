"""
Modulo de Documentos: upload, fase de assinatura e captura de documentos.

Endpoints principais:
    GET  /v2/documentos/upload-arquivo/gerar-url-upload/{tamanhoArquivo}
    POST /v2/documentos/fase-assinatura/enviar/servidor
    POST /v2/documentos/fase-assinatura/enviar/cidadao
    POST /v2/documentos/fase-assinatura/assinar/{id}
    GET  /v2/documentos/{id}
    POST /v2/documentos/paginated-search
"""

from __future__ import annotations

import os
import logging
from typing import Any, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from ..client import EDocsClient

logger = logging.getLogger("edocs_api.documentos")


class DocumentosModule:
    """Gerenciamento de documentos no E-Docs."""

    def __init__(self, client: EDocsClient):
        self._client = client

    # ── Upload de Arquivo ────────────────────────────────────

    def gerar_url_upload(self, tamanho_arquivo: int) -> dict:
        """
        Passo 1: Gera uma URL na nuvem do E-Docs para envio do arquivo.

        Args:
            tamanho_arquivo: Tamanho exato do arquivo em bytes.

        Returns:
            dict com 'url', 'body' (campos do formulario) e 'idArquivo'.
        """
        return self._client.get(
            f"/v2/documentos/upload-arquivo/gerar-url-upload/{tamanho_arquivo}"
        )

    def enviar_arquivo(self, upload_data: dict, caminho_arquivo: str) -> None:
        """
        Passo 2: Envia o arquivo fisico para a URL de upload (MinIO/S3).

        Args:
            upload_data: dict retornado por gerar_url_upload() contendo 'url' e 'body'
            caminho_arquivo: caminho local do arquivo PDF a ser enviado
        """
        url = upload_data["url"]
        body_fields = upload_data["body"]

        with open(caminho_arquivo, "rb") as f:
            files = {"file": (os.path.basename(caminho_arquivo), f, "application/octet-stream")}
            resp = requests.post(url, data=body_fields, files=files, timeout=self._client.config.timeout)

        if resp.status_code not in (200, 204):
            raise RuntimeError(
                f"Falha ao enviar arquivo para {url}: {resp.status_code} - {resp.text}"
            )
        logger.info("Arquivo enviado com sucesso para a nuvem do E-Docs.")

    def upload_arquivo(self, caminho_arquivo: str) -> str:
        """
        Metodo conveniencia: Passo 1 + Passo 2 do upload.

        Args:
            caminho_arquivo: caminho local do arquivo PDF

        Returns:
            idArquivo (UUID) para uso nas etapas seguintes.
        """
        tamanho = os.path.getsize(caminho_arquivo)
        upload_data = self.gerar_url_upload(tamanho)
        self.enviar_arquivo(upload_data, caminho_arquivo)
        return upload_data["idArquivo"]

    # ── Fase de Assinatura ───────────────────────────────────

    def enviar_como_servidor(
        self,
        id_arquivo: str,
        id_papel: str,
        id_classe_documental: str,
        resumo: str,
        valor_legal: str = "Original",
        natureza: str = "NatoDigital",
        genero: str = "Textual",
        restricao_acesso: dict | None = None,
    ) -> dict:
        """
        Cria um Documento em Fase de Assinatura como Servidor (assinatura unica do capturador).

        Args:
            id_arquivo: UUID do arquivo na nuvem
            id_papel: UUID do papel do servidor (via GET /v2/usuario/papeis)
            id_classe_documental: UUID da classe documental
            resumo: descricao/resumo do documento
            valor_legal: Original | CopiaAutenticadaAdministrativamente | CopiaSimples
            natureza: NatoDigital | Digitalizado
            genero: Textual
            restricao_acesso: dict com restricao de acesso

        Returns:
            dict com 'idEvento' e 'capturado'
        """
        payload: dict[str, Any] = {
            "idArquivo": id_arquivo,
            "idPapel": id_papel,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
            "valorLegal": valor_legal,
            "natureza": natureza,
            "genero": genero,
        }
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post("/v2/documentos/fase-assinatura/enviar/servidor", json=payload)

    def enviar_como_cidadao(
        self,
        id_arquivo: str,
        id_classe_documental: str,
        resumo: str,
        valor_legal: str = "Original",
        natureza: str = "NatoDigital",
        genero: str = "Textual",
        restricao_acesso: dict | None = None,
    ) -> dict:
        """
        Cria um Documento em Fase de Assinatura como Cidadao.

        Args:
            id_arquivo: UUID do arquivo na nuvem
            id_classe_documental: UUID da classe documental
            resumo: descricao/resumo do documento
            valor_legal: Original | CopiaAutenticadaAdministrativamente | CopiaSimples
            natureza: NatoDigital | Digitalizado
            genero: Textual
            restricao_acesso: dict com restricao de acesso

        Returns:
            dict com dados do documento assinado
        """
        payload: dict[str, Any] = {
            "idArquivo": id_arquivo,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
            "valorLegal": valor_legal,
            "natureza": natureza,
            "genero": genero,
        }
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post("/v2/documentos/fase-assinatura/enviar/cidadao", json=payload)

    def enviar_com_multiplos_assinantes_servidor(
        self,
        id_arquivo: str,
        id_papel: str,
        id_classe_documental: str,
        resumo: str,
        assinantes: list[dict],
        valor_legal: str = "Original",
        natureza: str = "NatoDigital",
        genero: str = "Textual",
        restricao_acesso: dict | None = None,
    ) -> str:
        """
        Cria um Documento em Fase de Assinatura com multiplos assinantes (Servidor).

        Args:
            id_arquivo: UUID do arquivo na nuvem
            id_papel: UUID do papel do servidor capturador
            id_classe_documental: UUID da classe documental
            resumo: descricao/resumo
            assinantes: lista de dicts, ex: [{"tipo": "Servidor", "idPapel": "uuid"}]
            valor_legal, natureza, genero: metadados do documento
            restricao_acesso: dict com restricao de acesso

        Returns:
            UUID do documento em fase de assinatura (idDocumentoFaseAssinatura)
        """
        payload: dict[str, Any] = {
            "idArquivo": id_arquivo,
            "idPapel": id_papel,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
            "valorLegal": valor_legal,
            "natureza": natureza,
            "genero": genero,
            "assinantes": assinantes,
        }
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post(
            "/v2/documentos/capturar/nato-digital/auto-assinado/servidor",
            json=payload,
        )

    def assinar_documento(self, id_documento_fase_assinatura: str) -> dict:
        """
        Assina um documento em fase de assinatura.

        Args:
            id_documento_fase_assinatura: UUID do documento em fase de assinatura

        Returns:
            dict com resultado da assinatura (capturado, idCapturaEvento, etc.)
        """
        return self._client.post(
            f"/v2/documentos/fase-assinatura/assinar/{id_documento_fase_assinatura}"
        )

    # ── Captura Direta ───────────────────────────────────────

    def capturar_nato_digital_auto_assinado_servidor(
        self,
        id_arquivo: str,
        id_papel: str,
        id_classe_documental: str,
        resumo: str,
        assinantes: list[dict],
        valor_legal: str = "Original",
        genero: str = "Textual",
        restricao_acesso: dict | None = None,
    ) -> str:
        """
        Captura documento nato-digital com assinatura eletronica (multiplos assinantes) - Servidor.

        Returns:
            idEvento (UUID) para acompanhamento
        """
        payload: dict[str, Any] = {
            "idArquivo": id_arquivo,
            "idPapel": id_papel,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
            "valorLegal": valor_legal,
            "natureza": "NatoDigital",
            "genero": genero,
            "assinantes": assinantes,
        }
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post(
            "/v2/documentos/capturar/nato-digital/auto-assinado/servidor",
            json=payload,
        )

    def capturar_digitalizado_servidor(
        self,
        id_arquivo: str,
        id_papel: str,
        id_classe_documental: str,
        resumo: str,
        valor_legal: str = "Original",
        restricao_acesso: dict | None = None,
    ) -> str:
        """
        Captura documento digitalizado (scan) - Servidor.

        Returns:
            idEvento (UUID) para acompanhamento
        """
        payload: dict[str, Any] = {
            "idArquivo": id_arquivo,
            "idPapel": id_papel,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
            "valorLegal": valor_legal,
            "natureza": "Digitalizado",
            "genero": "Textual",
        }
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post(
            "/v2/documentos/capturar/digitalizado/servidor",
            json=payload,
        )

    def capturar_digitalizado_cidadao(
        self,
        id_arquivo: str,
        id_classe_documental: str,
        resumo: str,
        valor_legal: str = "Original",
        restricao_acesso: dict | None = None,
    ) -> str:
        """Captura documento digitalizado - Cidadao."""
        payload: dict[str, Any] = {
            "idArquivo": id_arquivo,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
            "valorLegal": valor_legal,
            "natureza": "Digitalizado",
            "genero": "Textual",
        }
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post(
            "/v2/documentos/capturar/digitalizado/cidadao",
            json=payload,
        )

    def capturar_nato_digital_icp_servidor(
        self,
        id_arquivo: str,
        id_papel: str,
        id_classe_documental: str,
        resumo: str,
        valor_legal: str = "Original",
        restricao_acesso: dict | None = None,
    ) -> str:
        """Captura documento nato-digital com assinatura ICP-Brasil - Servidor."""
        payload: dict[str, Any] = {
            "idArquivo": id_arquivo,
            "idPapel": id_papel,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
            "valorLegal": valor_legal,
            "natureza": "NatoDigital",
            "genero": "Textual",
        }
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post(
            "/v2/documentos/capturar/nato-digital/icp-brasil/servidor",
            json=payload,
        )

    # ── Consultas ────────────────────────────────────────────

    def obter_documento(self, id_documento: str) -> dict:
        """Retorna os dados de um documento capturado."""
        return self._client.get(f"/v2/documentos/{id_documento}")

    def obter_metadados(self, id_documento: str) -> dict:
        """Retorna os metadados de um documento capturado."""
        return self._client.get(f"/v2/documentos/{id_documento}/metadados")

    def obter_fase_assinatura(self, id_documento_fase: str) -> dict:
        """Retorna dados de um documento em fase de assinatura."""
        return self._client.get(f"/v2/documentos/fase-assinatura/{id_documento_fase}")

    def buscar_documentos(
        self,
        filtro: dict | None = None,
        pagina: int = 1,
        tamanho_pagina: int = 20,
    ) -> dict:
        """
        Busca documentos capturados com filtros.

        Args:
            filtro: dict com campos de filtro (ex: {"resumo": "solicitacao"})
            pagina: numero da pagina
            tamanho_pagina: itens por pagina

        Returns:
            Resultado paginado
        """
        payload = filtro or {}
        payload["pagina"] = pagina
        payload["tamanhoPagina"] = tamanho_pagina
        return self._client.post("/v2/documentos/paginated-search", json=payload)
