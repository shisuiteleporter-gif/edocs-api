"""
Modulo de Agente: consulta a estrutura organizacional do E-Docs.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import EDocsClient


class AgenteModule:
    """Consultas de estruturas organizacionais (agentes)."""

    def __init__(self, client: EDocsClient):
        self._client = client

    def listar_patriarcas(self) -> list[dict]:
        """Retorna a lista de todos os patriarcas habilitados no E-Docs."""
        return self._client.get("/v2/agente/patriarcas")

    def listar_organizacoes(self, id_patriarca: str) -> list[dict]:
        """Retorna as organizacoes (orgaos) ativas de um patriarca."""
        return self._client.get(f"/v2/agente/{id_patriarca}/organizacoes")

    def listar_setores(self, id_orgao: str) -> list[dict]:
        """Retorna os setores ativos de uma organizacao."""
        return self._client.get(f"/v2/agente/{id_orgao}/setores")

    def listar_grupos_trabalho(self, id_orgao: str) -> list[dict]:
        """Retorna os grupos de trabalho ativos de uma organizacao."""
        return self._client.get(f"/v2/agente/{id_orgao}/grupos-trabalho")

    def listar_comissoes(self, id_orgao: str) -> list[dict]:
        """Retorna as comissoes ativas de uma organizacao."""
        return self._client.get(f"/v2/agente/{id_orgao}/comissoes")

    def hierarquia_completa(self) -> list[dict]:
        """Percorre toda a hierarquia: patriarcas -> orgaos -> setores."""
        resultado = []
        for patriarca in self.listar_patriarcas():
            entry_p = dict(patriarca)
            entry_p["organizacoes"] = []
            try:
                orgaos = self.listar_organizacoes(patriarca["id"])
                for org in orgaos:
                    entry_o = dict(org)
                    try:
                        entry_o["setores"] = self.listar_setores(org["id"])
                    except Exception:
                        entry_o["setores"] = []
                    entry_p["organizacoes"].append(entry_o)
            except Exception:
                pass
            resultado.append(entry_p)
        return resultado
