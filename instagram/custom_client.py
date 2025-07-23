from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Callable, Awaitable, Optional

import aiohttp
from urllib.parse import urlencode

from common.instagram.schemas import Message
from common.instagram.logger import logger


class IntagramClient:

    __allowed_methods = ["GET", "POST", "PATCH"]

    def __init__(
        self, async_session_factory: Callable[[], Awaitable[aiohttp.ClientSession]]
    ) -> None:
        self._async_sessions_factory: aiohttp.ClientSession = async_session_factory
        self._base_url = "https://graph.instagram.com/"

    @asynccontextmanager
    async def __call__(self, method: str, url: str, **kwargs):
        if method not in self.__allowed_methods:
            raise ValueError(f"Method '{method}' is not allowed for API calls")

        async with self._async_sessions_factory() as session:
            async with session.request(method, url, **kwargs) as response:
                yield response

    async def _get_access_token_from_oauth(
        self, auth_code, app_id, app_secret, redirect_url
    ) -> str:
        url = "https://api.instagram.com/oauth/access_token"
        payload = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_url,
            "code": auth_code,
        }
        try:
            async with self("POST", url, data=payload) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("access_token")
        except Exception as e:
            logger.exception("Error exchanging auth code for access token: %s", e)
            return None

    async def _subscribe_to_instagram_app(
        self, app_id, access_token: str
    ) -> str:
        url = f"{self._base_url}v23.0/{app_id}/subscribed_apps?subscribed_fields=messages&access_token={access_token}"
        try:
            async with self("POST", url) as response:
                response.raise_for_status()
                data = await response.json()
                return True
        except Exception as e:
            logger.exception(f"Error during subscription to app: {e}")
            return False
        
    async def _exchange_for_long_lived_token_display(
        self, short_lived_token: str, app_secret: str
    ) -> str | None:
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": app_secret,
            "access_token": short_lived_token,
        }
        url = f"{self._base_url}access_token?{urlencode(params)}"
        try:
            async with self("GET", url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("access_token")
            
        except Exception as e:
            logger.exception(
                "Error exchanging Display token for long-lived token: %s", e
            )
            return None

    async def _get_new_access_token(self, access_token: str):
        url = f"{self._base_url}refresh_access_token?grant_type=ig_refresh_token&access_token={access_token}"
        try:
            async with self("GET", url) as response:
                data = await response.json()
                return data.get("access_token")
        except Exception as e:
            logger.exception("Error during attempt to get info about user:%s", e)
            return {}

    async def _get_ig_user_info(self, user_id: str, access_token: str) -> dict:
        url = f"{self._base_url}{user_id}?fields=name,username,profile_pic&access_token={access_token}"
        try:
            async with self("GET", url) as response:
                data = await response.json()
                return data
        except Exception as e:
            logger.exception("Error during attempt to get info about user:%s", e)
            return {}

    async def _get_ig_user_id(self, access_token: str) -> Optional[str]:
        url = (
            f"{self._base_url}me?fields=user_id,id,username&access_token={access_token}"
        )
        try:
            async with self("GET", url) as response:
                data = await response.json()
                return data.get("user_id")

        except Exception as e:
            logger.error(f"Error during attempt to get essential info for ig:{e}")
            return None

    async def _get_user_id(self, access_token: str) -> Optional[str]:
        url = f"{self._base_url}me?fields=id,username&access_token={access_token}"
        try:
            async with self("GET", url) as response:
                data = await response.json()
                return data.get("id")

        except Exception as e:
            logger.exception("Error during attempt to get essential info for ig:%s", e)
            return None

    async def send_message(
        self,
        message: str,
        access_token: str,
        chat_id: str,
        is_sent_by_bot: bool = True,
        is_sent_by_service: bool = False,
        timeout: float | None = 10,
        *args,
        **kwargs,
    ) -> Message | None:
        user_id = await self._get_user_id(access_token)
        if user_id is None:
            logger.error("Error during attempt to send message to ig, user_id is None")
            return None

        url = f"{self._base_url}{user_id}/messages"
        payload = {
            "recipient": {"id": chat_id},
            "message": {"text": message},
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        output = None

        try:
            async with self("POST", url, json=payload, headers=headers) as response:
                output = await response.json()
                response.raise_for_status()

        except Exception as e:
            logger.exception(
                "erorr during attemt to send message by ig %s, reponse:%s", e, output
            )
            return None

        return Message(
            chat_id=chat_id,
            message=message,
            date=datetime.now(timezone.utc),
            is_sent_by_bot=is_sent_by_bot,
            is_sent_by_service=is_sent_by_service,
        )

    def get_session_factory(self):
        return self._async_sessions_factory
