"""
Exceções personalizadas para a API do E-Docs.
"""


class EDocsError(Exception):
    """Erro base do E-Docs."""

    def __init__(self, message: str, status_code: int | None = None, response_body: str | None = None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class EDocsAuthError(EDocsError):
    """Erro de autenticação (token inválido, expirado, escopo insuficiente)."""
    pass


class EDocsAPIError(EDocsError):
    """Erro genérico da API E-Docs."""
    pass


class EDocsNotFoundError(EDocsError):
    """Recurso não encontrado (404)."""
    pass


class EDocsValidationError(EDocsError):
    """Erro de validação (400 - bad request)."""
    pass
