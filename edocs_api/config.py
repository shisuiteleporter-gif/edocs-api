"""
Configuração do cliente E-Docs.

Gerencia as credenciais e endpoints da API.
"""

import os
from dataclasses import dataclass, field
from typing import Literal


AmbienteType = Literal["treinamento", "producao"]

URLS: dict[AmbienteType, str] = {
    "treinamento": "https://api.treinamento.e-docs.es.gov.br",
    "producao": "https://api.e-docs.es.gov.br",
}

URL_TOKEN = "https://acessocidadao.es.gov.br/is/connect/token"
URL_AUTHORIZE = "https://acessocidadao.es.gov.br/is/connect/authorize"


@dataclass
class EDocsConfig:
    """
    Configuração para o cliente da API E-Docs.

    Pode ser carregada de variáveis de ambiente ou passada diretamente.

    Variáveis de ambiente:
        EDOCS_CLIENT_ID     (obrigatório)
        EDOCS_CLIENT_SECRET (obrigatório)
        EDOCS_AMBIENTE      (opcional: "treinamento" ou "producao", default "treinamento")
        EDOCS_SCOPE         (opcional, default "api-sigades-consultar")
    """

    client_id: str
    client_secret: str
    ambiente: AmbienteType = "treinamento"
    scope: str = "api-sigades-consultar"
    timeout: int = 30

    # URLs internas (preenchidas automaticamente)
    base_url: str = ""
    token_url: str = URL_TOKEN
    authorize_url: str = URL_AUTHORIZE

    def __post_init__(self):
        if not self.client_id:
            raise ValueError("client_id é obrigatório")
        if not self.client_secret:
            raise ValueError("client_secret é obrigatório")
        self.base_url = URLS.get(self.ambiente, URLS["treinamento"])

    @classmethod
    def from_env(cls) -> "EDocsConfig":
        """Carrega a configuração das variáveis de ambiente."""
        client_id = os.environ.get("EDOCS_CLIENT_ID")
        client_secret = os.environ.get("EDOCS_CLIENT_SECRET")
        ambiente = os.environ.get("EDOCS_AMBIENTE", "treinamento")
        scope = os.environ.get("EDOCS_SCOPE", "api-sigades-consultar")

        if not client_id or not client_secret:
            raise ValueError(
                "As variáveis de ambiente EDOCS_CLIENT_ID e EDOCS_CLIENT_SECRET "
                "são obrigatórias. Crie um arquivo .env ou exporte-as."
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            ambiente=ambiente,  # type: ignore
            scope=scope,
        )
