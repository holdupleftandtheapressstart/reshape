class CRUDBadRequestError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class CRUDInternalError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
