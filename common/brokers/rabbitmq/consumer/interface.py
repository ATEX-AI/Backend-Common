import json
import asyncio
import logging

from aio_pika import Channel, Queue

from common.brokers.rabbitmq.connection_pool import ConnectionPool
from common.brokers.tasks.schema import Task


class ConsumerBasicInterface:
    RECONNECT_DELAY = 3  # seconds
    # Abort after this many consecutive connection failures so a
    # misconfigured broker (wrong password, removed user) does not
    # hide forever behind a silent reconnect loop.
    MAX_CONSECUTIVE_CONNECT_FAILURES = 20

    def __init__(self, broker_host_url: str, queue_name: str, logger: logging.Logger, prefetch_count: int = 1):
        self._broker_host_url = broker_host_url
        self._queue_name = queue_name
        self._prefetch_count = prefetch_count
        self._channel: Channel | None = None
        self._queue: Queue | None = None
        self._stopped = False
        self._logger = logger
        self._consecutive_connect_failures = 0

    @property
    def has_connection(self) -> bool:
        return self._channel is not None and not self._channel.is_closed

    def __getstate__(self):
        st = self.__dict__.copy()
        st.pop("_lock", None)
        return st

    def __setstate__(self, st):
        self.__dict__.update(st)
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        self._stopped = True

        if self._channel and not self._channel.is_closed:
            try:
                await self._channel.close()
            except Exception:
                pass
            self._channel = None
            self._queue = None

    async def connect(self) -> None:
        """Acquire a channel from the shared connection pool."""
        while not self.has_connection and not self._stopped:
            try:
                pool = await ConnectionPool.get_instance(self._broker_host_url)
                self._channel = await pool.acquire_channel(
                    prefetch_count=self._prefetch_count,
                )
                self._queue = await self._channel.declare_queue(
                    self._queue_name, durable=True
                )
                # Successful connect — reset failure counter.
                self._consecutive_connect_failures = 0
            except Exception as exc:
                self._consecutive_connect_failures += 1
                self._logger.warning(
                    "Error during %s connection (attempt %d/%d): %s",
                    self._broker_host_url,
                    self._consecutive_connect_failures,
                    self.MAX_CONSECUTIVE_CONNECT_FAILURES,
                    exc,
                )
                self._channel = None
                self._queue = None
                if self._consecutive_connect_failures >= self.MAX_CONSECUTIVE_CONNECT_FAILURES:
                    self._logger.critical(
                        "RabbitMQ consumer giving up on %s after %d failures. "
                        "Check credentials/network; the consumer will stop.",
                        self._broker_host_url,
                        self._consecutive_connect_failures,
                    )
                    self._stopped = True
                    return
                await asyncio.sleep(self.RECONNECT_DELAY)

    async def get_messages(self):
        while not self._stopped:
            await self.connect()
            if not self._channel or self._channel.is_closed:
                await asyncio.sleep(self.RECONNECT_DELAY)
                continue

            if not self._queue:
                await asyncio.sleep(self.RECONNECT_DELAY)
                continue

            try:
                async with self._queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        if self._stopped:
                            break

                        async with message.process():
                            try:
                                raw_str = message.body.decode("utf-8")
                                payload = json.loads(raw_str)

                                if isinstance(payload, str):
                                    task_dict = json.loads(payload)
                                else:
                                    task_dict = payload

                                yield Task(**task_dict)
                            except json.JSONDecodeError as e:
                                self._logger.error(f"JSON decode error: {e}")

            except Exception as e:
                self._logger.warning("Error during messages receiving %s", e)
                # Only close the channel, not the shared connection
                if self._channel and not self._channel.is_closed:
                    try:
                        await self._channel.close()
                    except Exception:
                        pass
                self._channel = None
                self._queue = None

            await asyncio.sleep(1.0)
