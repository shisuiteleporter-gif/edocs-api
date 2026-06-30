"""
Cliente principal da API E-Docs.

Gerencia autenticacao OAuth 2.0 e disponibiliza acesso a todos os modulos.
"""

from __future__ import annotations

import time
import logging
from typing import Any
from urllib.parse import urljoin

import requests

from .config import EDocsConfig
from .exceptions import EDocsAuthError, EDocsAPIError, EDocsNotFoundError, EDocsValidationError

logger = logging.getLogger("edocs_api")


class EDocsClient:
    """
    Cliente HTTP para a API publica do E-Docs.

    Uso basico:
        config = EDocsConfig(client_id="...", client_secret="...", scope="api-sigades-consultar")
        client = EDocsClient(config)
        patriarcas = client.get("/v2/agente/patriarcas")
    """

    def __init__(self, config: EDocsConfig):
        self.config = config
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "User-Agent": "EDocs-API-Client/0.1.0",
        })

        # Modulos (inicializados sob demanda)
        self._agente = None
        self._documentos = None
        self._encaminhamentos = None
        self._processos = None
        self._classificacao = None
        self._consultas = None

    # ── Propriedades dos modulos ───────────────────────────────

    @property
    def agente(self):
        if self._agente is None:
            from .modules.agente import AgenteModule
            self._agente = AgenteModule(self)
        return self._agente

    @property
    def documentos(self):
        if self._documentos is None:
            from .modules.documentos import DocumentosModule
            self._documentos = DocumentosModule(self)
        return self._documentos

    @property
    def encaminhamentos(self):
        if self._encaminhamentos is None:
            from .modules.encaminhamentos import EncaminhamentosModule
            self._encaminhamentos = EncaminhamentosModule(self)
        return self._encaminhamentos

    @property
    def processos(self):
        if self._processos is None:
            from .modules.processos import ProcessosModule
            self._processos = ProcessosModule(self)
        return self._processos

    @property
    def classificacao(self):
        if self._classificacao is None:
            from .modules.classificacao import ClassificacaoDocumentalModule
            self._classificacao = ClassificacaoDocumentalModule(self)
        return self._classificacao

    @property
    def consultas(self):
        if self._consultas is None:
            from .modules.consultas import ConsultasModule
            self._consultas = ConsultasModule(self)
        return self._consultas

    # ── Autenticacao ──────────────────────────────────────────

    def _authenticate(self):
        """Obtem um token de acesso via Client Credentials (fluxo OAuth 2.0)."""
        logger.info("Solicitando novo token de acesso...")
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "scope": self.config.scope,
        }
        resp = requests.post(
            self.config.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.config.timeout,
        )
        if resp.status_code != 200:
            raise EDocsAuthError(
                f"Falha na autenticacao: {resp.status_code} - {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        token_data = resp.json()
        self._access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = time.time() + expires_in - 60  # margem de 60s
        self._session.headers.update({
            "Authorization": f"Bearer {self._access_token}"
        })
        logger.info("Token obtido com sucesso.")

    def _ensure_token(self):
        """Verifica se o token ainda e valido, renovando se necessario."""
        if not self._access_token or time.time() >= self._token_expires_at:
            self._authenticate()

    # ── Metodos HTTP ─────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Executa uma requisicao HTTP, renovando token se necessario."""
        self._ensure_token()
        url = urljoin(self.config.base_url, path.lstrip("/"))
        kwargs.setdefault("timeout", self.config.timeout)
        resp = self._session.request(method, url, **kwargs)

        if resp.status_code in (401, 403):
            # Tenta renovar o token uma vez
            logger.info("Token pode ter expirado. Renovando...")
            self._authenticate()
            resp = self._session.request(method, url, **kwargs)

        return resp

    def get(self, path: str, params: dict | None = None, **kwargs: Any) -> Any:
        """GET request."""
        resp = self._request("GET", path, params=params, **kwargs)
        self._check_response(resp)
        return resp.json() if resp.content else None

    def post(self, path: str, json: dict | None = None, data: Any = None, **kwargs: Any) -> Any:
        """POST request."""
        resp = self._request("POST", path, json=json, data=data, **kwargs)
        self._check_response(resp)
        if not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def post_raw(self, path: str, **kwargs: Any) -> requests.Response:
        """POST request que retorna a response crua (para upload de arquivos)."""
        resp = self._request("POST", path, **kwargs)
        self._check_response(resp)
        return resp

    def _check_response(self, resp: requests.Response):
        """Valida o codigo HTTP da resposta."""
        if resp.status_code == 200 or resp.status_code == 202:
            return
        if resp.status_code == 204:
            return
        if resp.status_code == 400:
            raise EDocsValidationError(
                f"Erro de validacao: {resp.text}",
                status_code=400,
                response_body=resp.text,
            )
        if resp.status_code == 401:
            raise EDocsAuthError(
                f"Nao autorizado: {resp.text}",
                status_code=401,
                response_body=resp.text,
            )
        if resp.status_code == 403:
            raise EDocsAuthError(
                f"Acesso negado (escopo insuficiente): {resp.text}",
                status_code=403,
                response_body=resp.text,
            )
        if resp.status_code == 404:
            raise EDocsNotFoundError(
                f"Recurso nao encontrado: {resp.text}",
                status_code=404,
                response_body=resp.text,
            )
        if resp.status_code >= 500:
            raise EDocsAPIError(
                f"Erro interno do servidor: {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )

    # ── Metodos auxiliares ───────────────────────────────────

    def consultar_evento(self, id_evento: str) -> dict:
        """
        Consulta o status de um evento assincrono.

        Uso:
            status = client.consultar_evento("f1e2d3c4-...")
            # status["status"] pode ser "Pendente", "Executado", "Erro"
        """
        return self.get(f"/v2/eventos/{id_evento}")

    def aguardar_evento(self, id_evento: str, intervalo: float = 2.0, timeout: float = 120.0) -> dict:
        """
        Aguarda ate que um evento assincrono seja processado (polling).

        Args:
            id_evento: UUID do evento
            intervalo: segundos entre cada consulta
            timeout: tempo maximo de espera em segundos

        Returns:
            dict com os dados do evento processado
        """
        import time as time_module
        inicio = time_module.time()
        while True:
            if time_module.time() - inicio > timeout:
                raise TimeoutError(
                    f"Evento {id_evento} nao foi processado em {timeout}s"
                )
            evento = self.consultar_evento(id_evento)
            status = evento.get("status", "")
            if status == "Executado":
                logger.info(f"Evento {id_evento} executado com sucesso.")
                return evento
            if status == "Erro":
                raise EDocsAPIError(
                    f"Evento {id_evento} falhou: {evento.get('mensagem', 'sem detalhes')}"
                )
            logger.debug(f"Evento {id_evento} ainda pendente...")
            time_module.sleep(intervalo)
