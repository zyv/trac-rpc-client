from trac_rpc.models import TracRpcErrorResponse


class TracRpcError(Exception):
    def __init__(self, message: str, *, error: TracRpcErrorResponse = None):
        super().__init__(message)
        self._error = error

    @property
    def error(self) -> TracRpcErrorResponse:
        return self._error
