import logging
from typing import TypeVar

import requests
from .base import JWTAuthentication


T = TypeVar("T")

logger = logging.getLogger(__name__)


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
        try:
            response = requests.get(self.public_key_endpoint, timeout=10)
            response.raise_for_status()
            self.public_key = response.json().get("public_key")
        except requests.RequestException as e:
            logger.error("Failed to fetch JWT public key from %s: %s", self.public_key_endpoint, e)
            raise
        return self.public_key

    async def aget_public_key(self) -> str:
        """Async version for FastAPI/async frameworks. Uses aiohttp."""
        if self.public_key is not None:
            return self.public_key
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(self.public_key_endpoint, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self.public_key = data.get("public_key")
        except Exception as e:
            logger.error("Failed to fetch JWT public key from %s: %s", self.public_key_endpoint, e)
            raise
        return self.public_key
