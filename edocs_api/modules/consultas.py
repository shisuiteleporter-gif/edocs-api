"""
Modulo de Consultas: endpoints de apoio e consulta.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import EDocsClient


class ConsultasModule:
    """Consultas de apoio: fundamentos legais, associacoes, etc."""

    def __init__(self, client: EDocsClient):
        self._client = client

    def fundamentos_legais(self, id_patriarca: str) -> list[dict]:
        """
        Retorna os fundamentos legais de um patriarca.
        Usado para preencher restricoes de acesso.
        """
        return self._client.get(f"/v2/fundamentos-legais/{id_patriarca}")

    def papeis_usuario(self) -> list[dict]:
        """
        Retorna a lista de papeis (lotacoes) do usuario logado.
        Essencial para saber qual 'idPapel' usar nas operacoes.
        """
        return self._client.get("/v2/usuario/papeis")

    def dados_usuario(self) -> dict:
        """
        Retorna os dados do usuario autenticado.
        """
        return self._client.get("/v2/usuario")

    # ── Eventos ──────────────────────────────────────────────

    def consultar_evento(self, id_evento: str) -> dict:
        """
        Consulta o status de um evento assincrono.
        """
        return self._client.get(f"/v2/eventos/{id_evento}")

    # ── Associacoes ──────────────────────────────────────────

    def buscar_associacoes(
        self,
        filtro: dict | None = None,
        pagina: int = 1,
        tamanho_pagina: int = 20,
    ) -> dict:
        """
        Lista todas as associacoes de acordo com filtro.
        """
        payload = filtro or {}
        payload["pagina"] = pagina
        payload["tamanhoPagina"] = tamanho_pagina
        return self._client.post("/v2/associacoes/search", json=payload)

    def buscar_processos_associados(
        self,
        filtro: dict | None = None,
        pagina: int = 1,
        tamanho_pagina: int = 20,
    ) -> dict:
        """
        Lista todos os processos inclusos na associacao.
        """
        payload = filtro or {}
        payload["pagina"] = pagina
        payload["tamanhoPagina"] = tamanho_pagina
        return self._client.post("/v2/associacoes/processos/search", json=payload)

    # ── Caixas ───────────────────────────────────────────────

    def papeis_para_encaminhamento(self, id_caixa: str) -> list[dict]:
        """Retorna papeis que podem responder/reencaminhar em uma caixa."""
        return self._client.get(f"/v2/caixas/{id_caixa}/encaminhamento/responder")

    def papeis_para_autuar(self, id_caixa: str) -> list[dict]:
        """Retorna papeis que podem autuar processo em uma caixa."""
        return self._client.get(f"/v2/caixas/{id_caixa}/processo/autuar")

    def papeis_para_despachar(self, id_caixa: str) -> list[dict]:
        """Retorna papeis que podem despachar processo em uma caixa."""
        return self._client.get(f"/v2/caixas/{id_caixa}/processo/despachar")

    def papeis_para_entranhar(self, id_caixa: str) -> list[dict]:
        """Retorna papeis que podem entranhar em processo em uma caixa."""
        return self._client.get(f"/v2/caixas/{id_caixa}/processo/entranhar")
