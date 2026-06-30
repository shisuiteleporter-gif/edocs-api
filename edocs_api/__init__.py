"""
E-Docs API - Cliente Python para API Pública do E-Docs (Governo ES)

Documentação oficial: https://docs.e-docs.es.gov.br/api/
Ambiente de Treinamento: https://api.treinamento.e-docs.es.gov.br
Ambiente de Produção: https://api.e-docs.es.gov.br
"""

__version__ = "0.1.0"
__author__ = "OpenWork"

from .client import EDocsClient
from .config import EDocsConfig
from .exceptions import (
    EDocsError,
    EDocsAuthError,
    EDocsAPIError,
    EDocsNotFoundError,
    EDocsValidationError,
)
