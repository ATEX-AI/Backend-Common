import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set, Type, Optional

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from common.redis.pubsub import (
    _EventRegistry,
    BaseEventType,
    ConnectionLike,
    EventPayload,
)


class EventSubscriber(_EventRegistry):

    PING_INTERVAL = timedelta(minutes=30)
    PING_TIMEOUT = 10
    CONNECTIONS_LIMIT = 50

    def __init__(
        self,
        redis: Redis,
        *,
        logger: logging.Logger,
        events_cls: Optional[Type[BaseEventType]] = None,
        events_payload_cls: Optional[Type[EventPayload]] = None,
    ) -> None:
        super().__init__(events_cls=events_cls, events_payload_cls=events_payload_cls)
        self._redis: Redis = redis
        self._pubsub: PubSub | None = None
        self._listener: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._logger = logger

        self._sessions: Dict[str, Set[ConnectionLike]] = {}
        self._session_channels: Dict[str, Set[str]] = {}
        self._last_active: Dict[ConnectionLike, datetime] = {}

    async def start(self) -> None:
        self._pubsub = self._redis.pubsub()
        await self._pubsub.psubscribe("*")
        self._listener = asyncio.create_task(self._listen())
        self._pinger = asyncio.create_task(self._ping_loop())

    async def stop(self) -> None:
        self._stop.set()
        if self._listener and not self._listener.done():
            self._listener.cancel()
        if self._pinger and not self._pinger.done():
            self._pinger.cancel()
        if self._pubsub:
            await self._pubsub.close()

        coros: List[asyncio.Task] = []
        for ws_set in self._sessions.values():
            for ws in ws_set:
                coros.append(
                    asyncio.create_task(self._safe_close(ws, 10001, "Server shutdown"))
                )
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

        self._sessions.clear()
        self._session_channels.clear()
        self._last_active.clear()

    async def subscribe_user(
        self,
        session_id: str,
        ws: ConnectionLike,
        *,
        channels: List[str],
        already_accepted: bool = True,
    ) -> None:
        if not already_accepted:
            await ws.accept()

        ws_set = self._sessions.setdefault(session_id, set())

        if ws not in ws_set and len(ws_set) >= self.CONNECTIONS_LIMIT:
            await self._safe_close(
                ws, 1008, f"Connection limit ({self.CONNECTIONS_LIMIT}) exceeded"
            )
            return

        if ws in ws_set:
            self._session_channels[ws].update(channels)
            self._last_active[ws] = datetime.now(timezone.utc)
            return

        ws_set.add(ws)
        self._session_channels[ws] = set(channels)
        self._last_active[ws] = datetime.now(timezone.utc)

    async def unsubscribe_user(
        self,
        session_id: str,
        ws: Optional[ConnectionLike] = None,
        *,
        channels: Optional[List[str]] = None,
        close_if_empty: bool = True,
    ) -> None:
        if session_id not in self._sessions:
            return

        targets: Set[ConnectionLike] = {ws} if ws else set(self._sessions[session_id])
        for conn in list(targets):
            if channels is None:
                await self._safe_close(conn, 1000, "Unsubscribed")
                self._remove_connection(session_id, conn)
            else:
                current = self._session_channels.get(conn, set())
                current.difference_update(channels)
                if not current and close_if_empty:
                    await self._safe_close(conn, 1000, "No channels remaining")
                    self._remove_connection(session_id, conn)
                else:
                    self._session_channels[conn] = current

        if not self._sessions.get(session_id):
            self._sessions.pop(session_id, None)

    async def _listen(self) -> None:
        assert self._pubsub is not None
        async for msg in self._pubsub.listen():
            if msg.get("type") != "pmessage":
                continue

            channel: str = (
                msg["channel"].decode()
                if isinstance(msg["channel"], bytes)
                else msg["channel"]
            )

            raw_txt = msg.get("data")
            try:
                raw = json.loads(
                    raw_txt.decode()
                    if isinstance(raw_txt, (bytes, bytearray))
                    else raw_txt
                )

                if not isinstance(raw, dict) or raw.get("destination") != "ws_event":
                    continue

                payload = self._events_payload_cls.model_validate(raw)
            except Exception as e:
                self._logger.warning("raw_data: %s; conv_err: %s", raw, e)
                continue

            if not self._is_registered(payload.event):
                self._logger.error("event isn't registered, raw data: %s", raw)
                continue

            await self._fanout(channel, raw_txt)
            if self._stop.is_set():
                break

    async def _fanout(self, channel: str, raw: str) -> None:
        now = datetime.now(timezone.utc)
        coros = []
        for conn, ch_set in self._session_channels.items():
            if channel in ch_set:
                coros.append(conn.send_text(raw))
                self._last_active[conn] = now
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

    async def _ping_loop(self) -> None:
        while not self._stop.is_set():
            await asyncio.sleep(self.PING_INTERVAL.total_seconds())
            now = datetime.now(timezone.utc)
            for session_id, conns in list(self._sessions.items()):
                for conn in list(conns):
                    last = self._last_active.get(conn, now)
                    if now - last < self.PING_INTERVAL:
                        continue

                    try:
                        await conn.send_text('{"type":"ping"}')
                        pong_task = asyncio.create_task(
                            conn.receive_text()
                        )  # TODO - think about this
                        done, _ = await asyncio.wait(
                            {pong_task},
                            timeout=self.PING_TIMEOUT,
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        if pong_task not in done or not pong_task.result():
                            raise TimeoutError("pong not received")

                        self._last_active[conn] = datetime.now(timezone.utc)

                    except Exception as e:
                        self._logger.info(f"Ping failed ({e}) - closing")
                        await self._safe_close(conn, 1001, "Ping timeout")
                        self._remove_connection(session_id, conn)

    async def _safe_close(self, ws: ConnectionLike, code: int, reason: str) -> None:
        try:
            await ws.close(code=code, reason=reason)
        except Exception as e:
            self._logger.info(f"Error closing websocket: {e}")

    def _remove_connection(self, session_id: str, ws: ConnectionLike) -> None:
        self._sessions.get(session_id, set()).discard(ws)
        self._session_channels.pop(ws, None)
        self._last_active.pop(ws, None)
        if not self._sessions.get(session_id):
            self._sessions.pop(session_id, None)
