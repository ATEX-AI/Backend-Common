import hashlib
import hmac
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Callable, Awaitable, Optional

import aiohttp
from urllib.parse import urlencode

from common.messenger.schemas import Message
from common.messenger.logger import logger


class MessengerClient:

    __allowed_methods = ["GET", "POST", "PATCH", "DELETE"]

    def __init__(
        self, async_session_factory: Callable[[], Awaitable[aiohttp.ClientSession]]
    ) -> None:
        self._async_sessions_factory: aiohttp.ClientSession = async_session_factory
        self._base_url = "https://graph.facebook.com/"
        self._api_version = "v23.0"

    @asynccontextmanager
    async def __call__(self, method: str, url: str, **kwargs):
        if method not in self.__allowed_methods:
            raise ValueError(f"Method '{method}' is not allowed for API calls")

        async with self._async_sessions_factory() as session:
            async with session.request(method, url, **kwargs) as response:
                yield response

    async def _get_user_access_token_from_oauth(
        self, auth_code: str, app_id: str, app_secret: str, redirect_url: str
    ) -> Optional[str]:
        params = {
            "client_id": app_id,
            "redirect_uri": redirect_url,
            "client_secret": app_secret,
            "code": auth_code,
        }
        url = f"{self._base_url}{self._api_version}/oauth/access_token?{urlencode(params)}"

        try:
            async with self("GET", url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("access_token")
        except Exception as e:
            logger.warning("Error exchanging auth code for user access token: %s", e)
            return None

    async def _exchange_for_long_lived_user_token(
        self, short_lived_user_token: str, app_id: str, app_secret: str
    ) -> Optional[str]:
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_lived_user_token,
        }
        url = f"{self._base_url}{self._api_version}/oauth/access_token?{urlencode(params)}"
        try:
            async with self("GET", url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("access_token")
        except Exception as e:
            logger.warning("Error exchanging user token for long-lived token: %s", e)
            return None

    async def _get_page_access_token_from_user_token(
        self, page_id: str, user_access_token: str, app_secret: str
    ) -> Optional[str]:
        h = hmac.new(
            app_secret.encode("utf-8"),
            msg=user_access_token.encode("utf-8"),
            digestmod=hashlib.sha256,
        )
        appsecret_proof = h.hexdigest()
        url = (
            f"{self._base_url}{self._api_version}/{page_id}"
            f"?fields=access_token&access_token={user_access_token}"
            f"&appsecret_proof{appsecret_proof}"
        )
        try:
            async with self("GET", url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("access_token")
        except Exception as e:
            logger.warning("Error fetching Page Access Token: %s", e)
            return None

    async def _subscribe_to_messenger_app(
        self, page_id: str, page_access_token: str
    ) -> bool:
        subscribed_fields = ",".join(
            [
                "messages",
                "messaging_postbacks",
                "messaging_optins",
                "message_deliveries",
                "message_reads",
                "messaging_referrals",
                "messaging_handovers",
                "messaging_account_linking",
                "messaging_policy_enforcement",
                "messaging_seen",
                "standby",
            ]
        )

        url = (
            f"{self._base_url}{self._api_version}/{page_id}/subscribed_apps"
            f"?subscribed_fields={subscribed_fields}"
            f"&access_token={page_access_token}"
        )
        try:
            async with self("POST", url) as response:
                response.raise_for_status()
                _ = await response.json()
                return True
        except Exception as e:
            logger.warning("Error during subscription to Messenger app: %s", e)
            return False

    async def _unsubscribe_from_messenger_app(
        self, page_id: str, page_access_token: str
    ) -> bool:
        url = (
            f"{self._base_url}{self._api_version}/{page_id}/subscribed_apps"
            f"?access_token={page_access_token}"
        )
        try:
            async with self("DELETE", url) as response:
                response.raise_for_status()
                _ = await response.json()
                return True
        except Exception as e:
            logger.warning("Error during unsubscription from Messenger app: %s", e)
            return False

    async def _get_page_info(self, page_id: str, access_token: str) -> dict:
        url = (
            f"{self._base_url}{self._api_version}/{page_id}"
            f"?fields=id,name,username&access_token={access_token}"
        )
        try:
            async with self("GET", url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.warning("Error fetching page info: %s", e)
            return {}

    async def _get_page_id(self, page_access_token: str) -> Optional[str]:
        url = f"{self._base_url}{self._api_version}/me?access_token={page_access_token}"
        try:
            async with self("GET", url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("id")
        except Exception as e:
            logger.warning("Error fetching page id from token: %s", e)
            return None

    async def send_message(
        self,
        message: str,
        page_access_token: str,
        recipient_id: str,
        is_sent_by_bot: bool = True,
        is_sent_by_service: bool = False,
        timeout: Optional[float] = 10,
        *args,
        **kwargs,
    ) -> Optional[Message]:
        page_id = await self._get_page_id(page_access_token)
        if page_id is None:
            logger.error("Error: could not resolve Page ID from provided access token")
            return None

        url = f"{self._base_url}{self._api_version}/me/messages?access_token={page_access_token}"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
        }
        headers = {"Content-Type": "application/json"}

        output = None
        try:
            async with self(
                "POST", url, json=payload, headers=headers, timeout=timeout
            ) as response:
                output = await response.json()
                response.raise_for_status()
        except Exception as e:
            logger.warning(
                "Error attempting to send Messenger message %s, response: %s", e, output
            )
            return None

        return Message(
            chat_id=recipient_id,
            message=message,
            date=datetime.now(timezone.utc),
            is_sent_by_bot=is_sent_by_bot,
            is_sent_by_service=is_sent_by_service,
        )

    def get_session_factory(self):
        return self._async_sessions_factory
