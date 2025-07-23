class BaseAuthenticationException(Exception):
    def __init__(self, message: str):
        self.message = message


class UnauthorizedAccess(BaseAuthenticationException): ...


class AccessForbidden(BaseAuthenticationException): ...
