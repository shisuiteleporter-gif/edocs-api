"""
Modulo de Encaminhamentos: criacao, resposta, reencaminhamento e complementacao.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import EDocsClient


class EncaminhamentosModule:
    """Gerenciamento de encaminhamentos no E-Docs."""

    def __init__(self, client: EDocsClient):
        self._client = client

    def novo(
        self,
        id_papel_remetente: str,
        destinatarios: list[dict],
        assunto: str,
        mensagem: str,
        documentos: list[str] | None = None,
        enviar_email: bool = False,
        restricao_acesso: dict | None = None,
    ) -> str:
        """
        Cria um novo encaminhamento.

        Args:
            id_papel_remetente: UUID do papel do remetente (servidor)
            destinatarios: lista de dicts [{"tipo": "Unidade", "id": "uuid"}, ...]
            assunto: assunto do encaminhamento
            mensagem: corpo da mensagem
            documentos: lista de UUIDs de documentos anexados
            enviar_email: se deve notificar por email
            restricao_acesso: dict com restricao de acesso

        Returns:
            idEvento (UUID) para acompanhamento
        """
        payload: dict[str, Any] = {
            "idPapelRemetente": id_papel_remetente,
            "destinatarios": destinatarios,
            "assunto": assunto,
            "mensagem": mensagem,
        }
        if documentos:
            payload["documentos"] = documentos
        if enviar_email:
            payload["enviarEmailNotificacoes"] = True
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post("/v2/encaminhamento/novo", json=payload)

    def responder(
        self,
        id_encaminhamento_origem: str,
        id_papel_remetente: str,
        mensagem: str,
        documentos: list[str] | None = None,
    ) -> str:
        """
        Responde a um encaminhamento recebido.

        Args:
            id_encaminhamento_origem: UUID do encaminhamento original
            id_papel_remetente: UUID do papel do remetente da resposta
            mensagem: texto da resposta
            documentos: lista de UUIDs de documentos anexados

        Returns:
            idEvento (UUID)
        """
        payload: dict[str, Any] = {
            "idEncaminhamentoOrigem": id_encaminhamento_origem,
            "idPapelRemetente": id_papel_remetente,
            "mensagem": mensagem,
        }
        if documentos:
            payload["documentos"] = documentos

        return self._client.post("/v2/encaminhamento/responder", json=payload)

    def reencaminhar(
        self,
        id_encaminhamento_origem: str,
        id_papel_remetente: str,
        destinatarios: list[dict],
        mensagem: str,
        documentos: list[str] | None = None,
    ) -> str:
        """
        Reencaminha um encaminhamento recebido para novo destino.

        Args:
            id_encaminhamento_origem: UUID do encaminhamento original
            id_papel_remetente: UUID do papel do remetente
            destinatarios: lista de dicts [{"tipo": "Unidade", "id": "uuid"}]
            mensagem: texto do reencaminhamento
            documentos: lista de UUIDs de documentos

        Returns:
            idEvento (UUID)
        """
        payload: dict[str, Any] = {
            "idEncaminhamentoOrigem": id_encaminhamento_origem,
            "idPapelRemetente": id_papel_remetente,
            "destinatarios": destinatarios,
            "mensagem": mensagem,
        }
        if documentos:
            payload["documentos"] = documentos

        return self._client.post("/v2/encaminhamento/reencaminhar", json=payload)

    def complementar(
        self,
        id_encaminhamento_origem: str,
        id_papel_remetente: str,
        mensagem: str,
        documentos: list[str] | None = None,
    ) -> str:
        """
        Adiciona informacoes complementares a um encaminhamento enviado.

        So funciona se o encaminhamento ainda nao foi respondido ou reencaminhado.

        Args:
            id_encaminhamento_origem: UUID do encaminhamento
            id_papel_remetente: UUID do papel do remetente
            mensagem: texto complementar
            documentos: lista de UUIDs de documentos

        Returns:
            idEvento (UUID)
        """
        payload: dict[str, Any] = {
            "idEncaminhamentoOrigem": id_encaminhamento_origem,
            "idPapelRemetente": id_papel_remetente,
            "mensagem": mensagem,
        }
        if documentos:
            payload["documentos"] = documentos

        return self._client.post("/v2/encaminhamento/complementar", json=payload)
