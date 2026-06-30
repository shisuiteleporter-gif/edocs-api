"""
Modulo de Processos: autuacao, despacho, avocamento, entranhamento, etc.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import EDocsClient


class ProcessosModule:
    """Gerenciamento de processos administrativos no E-Docs."""

    def __init__(self, client: EDocsClient):
        self._client = client

    def autuar(
        self,
        id_papel_autuador: str,
        id_classe_documental: str,
        resumo: str,
        interessados: list[dict] | None = None,
        documentos: list[str] | None = None,
        restricao_acesso: dict | None = None,
    ) -> str:
        """
        Cria (autua) um novo processo administrativo.

        Args:
            id_papel_autuador: UUID do papel do servidor que esta autuando
            id_classe_documental: UUID da classe documental do processo
            resumo: descricao/resumo do processo
            interessados: lista de interessados [{"tipo": "Servidor", "idPapel": "uuid"}, ...]
            documentos: lista de UUIDs de documentos para entranhar
            restricao_acesso: dict com restricao de acesso

        Returns:
            idEvento (UUID) para acompanhamento
        """
        payload: dict[str, Any] = {
            "idPapelAutuador": id_papel_autuador,
            "idClasseDocumental": id_classe_documental,
            "resumo": resumo,
        }
        if interessados:
            payload["interessados"] = interessados
        if documentos:
            payload["documentos"] = documentos
        if restricao_acesso:
            payload["restricaoAcesso"] = restricao_acesso

        return self._client.post("/v2/processos/autuar", json=payload)

    def despachar(
        self,
        id_processo: str,
        id_papel_autor: str,
        destino_custodiante: dict,
        mensagem: str,
        documentos: list[str] | None = None,
    ) -> str:
        """
        Despacha (movimenta) um processo para outro custodiante.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor autor do despacho
            destino_custodiante: dict {"tipo": "Unidade", "id": "uuid-orgao"}
            mensagem: texto do despacho
            documentos: lista de UUIDs de documentos

        Returns:
            idEvento (UUID)
        """
        payload: dict[str, Any] = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
            "destinoCustodiante": destino_custodiante,
            "mensagem": mensagem,
        }
        if documentos:
            payload["documentos"] = documentos

        return self._client.post("/v2/processos/despachar", json=payload)

    def avocar(
        self,
        id_processo: str,
        id_papel_autor: str,
        mensagem: str | None = None,
    ) -> str:
        """
        Avoca (retorna) o processo para o custodiante anterior.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor
            mensagem: justificativa (opicional)

        Returns:
            idEvento (UUID)
        """
        payload: dict[str, Any] = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
        }
        if mensagem:
            payload["mensagem"] = mensagem

        return self._client.post("/v2/processos/avocar", json=payload)

    def entranhar_documentos(
        self,
        id_processo: str,
        id_papel_autor: str,
        documentos: list[str],
    ) -> str:
        """
        Adiciona documentos a um processo sem movimenta-lo.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor
            documentos: lista de UUIDs de documentos

        Returns:
            idEvento (UUID)
        """
        payload = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
            "documentos": documentos,
        }
        return self._client.post("/v2/processos/entranhar-documentos", json=payload)

    def desentranhar_documentos(
        self,
        id_processo: str,
        id_papel_autor: str,
        documentos: list[str],
    ) -> str:
        """
        Remove documentos entranhados anteriormente.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor
            documentos: lista de UUIDs de documentos

        Returns:
            idEvento (UUID)
        """
        payload = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
            "documentos": documentos,
        }
        return self._client.post("/v2/processos/desentranhar", json=payload)

    def entranhar_encaminhamento(
        self,
        id_processo: str,
        id_papel_autor: str,
        id_encaminhamento: str,
    ) -> str:
        """
        Adiciona um encaminhamento e seus documentos ao processo.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor
            id_encaminhamento: UUID do encaminhamento

        Returns:
            idEvento (UUID)
        """
        payload = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
            "idEncaminhamento": id_encaminhamento,
        }
        return self._client.post("/v2/processos/entranhar-encaminhamento", json=payload)

    def editar(
        self,
        id_processo: str,
        id_papel_autor: str,
        dados_edicao: dict,
    ) -> str:
        """
        Edita informacoes do processo sem movimenta-lo.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor
            dados_edicao: dict com os campos a editar

        Returns:
            idEvento (UUID)
        """
        payload = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
            **dados_edicao,
        }
        return self._client.post("/v2/processos/editar", json=payload)

    def encerrar(
        self,
        id_processo: str,
        id_papel_autor: str,
        motivo: str,
    ) -> str:
        """
        Encerra (conclui) um processo.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor
            motivo: justificativa do encerramento

        Returns:
            idEvento (UUID)
        """
        payload = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
            "motivo": motivo,
        }
        return self._client.post("/v2/processos/encerrar", json=payload)

    def reabrir(
        self,
        id_processo: str,
        id_papel_autor: str,
        motivo: str,
    ) -> str:
        """
        Reabre um processo previamente encerrado.

        Args:
            id_processo: UUID do processo
            id_papel_autor: UUID do papel do servidor
            motivo: justificativa da reabertura

        Returns:
            idEvento (UUID)
        """
        payload = {
            "idProcesso": id_processo,
            "idPapelAutor": id_papel_autor,
            "motivo": motivo,
        }
        return self._client.post("/v2/processos/reabrir", json=payload)
