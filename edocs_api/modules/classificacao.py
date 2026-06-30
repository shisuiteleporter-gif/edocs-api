"""
Modulo de Classificacao Documental: planos e classes de classificacao.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import EDocsClient


class ClassificacaoDocumentalModule:
    """Consultas de planos e classes de classificacao documental."""

    def __init__(self, client: EDocsClient):
        self._client = client

    def listar_planos_ativos(self, id_patriarca: str) -> list[dict]:
        """
        Retorna os planos de classificacao ativos de um patriarca.

        Args:
            id_patriarca: UUID do patriarca
        """
        return self._client.get(
            f"/v2/classificacao-documental/{id_patriarca}/planos-ativos"
        )

    def listar_classes_ativas(self, id_plano: str) -> list[dict]:
        """
        Retorna as classes ativas de um plano de classificacao.

        Args:
            id_plano: UUID do plano
        """
        return self._client.get(
            f"/v2/classificacao-documental/{id_plano}/classes-ativas"
        )
