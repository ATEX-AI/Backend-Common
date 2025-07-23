import inspect
from abc import ABC, abstractmethod
from functools import wraps

from .base import Authentication
from .exceptions import AccessForbidden, UnauthorizedAccess


class SecretKeyAuthentication(Authentication, ABC):
    def __init__(self, auth_key: str, header_name: str = "x_authorization"):
        self.__auth_key = auth_key
        self.header_name = header_name

    def authenticate(self, auth_key: str) -> bool:
        return self.__auth_key == auth_key

    @abstractmethod
    def adjust_signature(self, sig, params):
        raise NotImplementedError

    def __call__(self, func, *args, **kwargs):
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        self.adjust_signature(sig, params)

        new_sig = sig.replace(parameters=params)

        @wraps(func)
        async def decorated_function(*args, **kwargs):
            x_auth_token = kwargs.pop(self.header_name)
            if x_auth_token is None:
                raise AccessForbidden(message="Service-Authorization header missing")

            if not self.authenticate(x_auth_token):
                raise UnauthorizedAccess(message=f"Invalid {self.header_name} header")

            return await func(*args, **kwargs)

        decorated_function.__signature__ = new_sig
        return decorated_function
