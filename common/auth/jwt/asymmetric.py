import logging
from typing import TypeVar

import requests
from .base import JWTAuthentication


T = TypeVar("T")


class JWTAsymmetricAuthentication(JWTAuthentication):

    def __init__(
        self,
        public_key_endpoint,
        logger: logging.Logger,
        algorithm: str = "ES256",
    ):
        self.public_key_endpoint = public_key_endpoint
        super().__init__(algorithms=[algorithm], logger=logger)

    def get_public_key(self) -> str:
        if self.public_key is not None:
            return self.public_key
        data = requests.get(self.public_key_endpoint)
        self.public_key = data.json().get("public_key")
