from backend.models import Error


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str, retryable: bool = False):
        self.status = status
        self.error = Error(code=code, message=message, retryable=retryable)
        super().__init__(code)


class ProviderError(Exception):
    """Only fixed safe codes cross the provider boundary; never raw error bodies."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
