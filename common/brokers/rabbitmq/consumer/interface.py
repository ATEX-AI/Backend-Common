import json
import asyncio
import logging

from aio_pika import connect_robust, Connection, Channel, Queue

from common.brokers.tasks.schema import Task


# logger = logging.getLogger(__file__)


class ConsumerBasicInterface:
    RECONNECT_DELAY = 3  # seconds

    def __init__(self, broker_host_url: str, queue_name: str, logger: logging.Logger, prefetch_count: int = 1):
        self._broker_host_url = broker_host_url
        self._queue_name = queue_name
        self._prefetch_count = prefetch_count
        self._connection: Connection | None = None
        self._channel: Channel | None = None
        self._queue: Queue | None = None
        self._stopped = False
        self._logger = logger

    @property
    def has_connection(self) -> bool:
        return self._connection is not None and not self._connection.is_closed

    def __getstate__(self):
        st = self.__dict__.copy()
        st.pop("_lock", None)
        return st

    def __setstate__(self, st):
        self.__dict__.update(st)
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        """
        Close the channel and the connection to RabbitMQ.
        """
        self._stopped = True
        
        if self._channel and not self._channel.is_closed:
            await self._channel.close()

        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def connect(self) -> None:
        """
        Create a robust connection and channel if we don't have one already.
        Retries if connection fails.
        """
        while not self.has_connection and not self._stopped:
            try:
                self._connection = await connect_robust(self._broker_host_url)
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=self._prefetch_count)
                self._queue = await self._channel.declare_queue(
                    self._queue_name, durable=True
                )
            except Exception as exc:
                self._logger.warning(f"Error during {self._broker_host_url} connection: {exc}")
                await asyncio.sleep(self.RECONNECT_DELAY)

    async def get_messages(self):
        """
        Async generator that yields messages as Task objects, with automatic reconnection.
        """
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
                                inner_json_str = json.loads(raw_str)
                                task_dict = json.loads(inner_json_str)
                                yield Task(**task_dict)
                            except json.JSONDecodeError as e:
                                ...

            except Exception as e:
                self._logger.warning("error during messages receiving %s", e)
                await self.close()

            await asyncio.sleep(1.0)
