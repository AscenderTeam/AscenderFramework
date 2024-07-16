class IncorrectSchemeError(Exception):
    def __str__(self) -> str:
        return "Identity Security Module requires OAuth2 Scheme to regenerate token by refresh token"