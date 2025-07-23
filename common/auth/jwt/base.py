import logging
import jwt
from abc import ABC, abstractmethod
from typing import TypeVar
from datetime import datetime, timezone

from common.auth.base import Authentication
from common.auth.exceptions import AccessForbidden, UnauthorizedAccess


T = TypeVar("T")


class JWTAuthentication(Authentication, ABC):

    def __init__(self, algorithms: list[str], logger: logging.Logger):
        self.public_key: str | None = None
        self.public_key_updating_date = datetime.now(timezone.utc)
        self.algorithms = algorithms
        self._logger = logger
    @abstractmethod
    def get_public_key(self) -> str:
        raise NotImplementedError

    def decode_token_by_public_key(self, auth_credentials) -> dict:
        try:
            token = auth_credentials.credentials

        except Exception as e:
            self._logger.warning("Error during token decoding occurred: %s", e)
            raise AccessForbidden(
                message="Token is invalid",
            )

        token = auth_credentials.credentials
        self.get_public_key()

        try:
            decoded_token = jwt.decode(
                token, self.public_key, algorithms=self.algorithms
            )
            return decoded_token
        
        except jwt.ExpiredSignatureError:
            raise UnauthorizedAccess(message="Token has expired")

        except jwt.InvalidTokenError:
            raise UnauthorizedAccess(message="Invalid token")

        except Exception:
            raise AccessForbidden(message="Token is invalid")

    def authenticate(
        self,
        auth_credentials,
        public_key_mode: bool = True,
        secret_key_mode: bool = False,
    ) -> "Authentication.AuthInfo":
        if public_key_mode:
            return self.wrap(
                self.AuthInfo, self.decode_token_by_public_key(auth_credentials)
            )

        if secret_key_mode:
            pass
