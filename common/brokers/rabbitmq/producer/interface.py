import json
import asyncio
import logging

from aio_pika import connect_robust, ExchangeType, Message


class ProducerBasicInterface:
    def __init__(self, broker_host_url: str, logger: logging.Logger):
        self._broker_host_url = broker_host_url
        self.__connection = None
        self.__channel = None
        self._exchange = None
        self._logger = logger
        self._lock = asyncio.Lock()

    @property
    def has_connection(self) -> bool:
        return self.__connection is not None and not self.__connection.is_closed

    @property
    def has_channel(self) -> bool:
        return self.__channel is not None and not self.__channel.is_closed

    async def connect(self) -> None:
        async with self._lock:
            if self.has_connection and self.has_channel:
                return

            try:
                if self.__connection:
                    await self.close()
            except Exception:
                pass

            try:
                self.__connection = await connect_robust(self._broker_host_url)
                self.__channel = await self.__connection.channel()
                self._exchange = await self.__channel.declare_exchange(
                    "DirectExchange", ExchangeType.DIRECT, durable=True
                )
            except Exception as e:
                self._logger.warning(f"Error during {self._broker_host_url} connection: {e}")
                self.__connection = None
                self.__channel = None
                self._exchange = None

    async def send_task(self, worker: str, task_payload: dict):
        if not (self.has_connection and self.has_channel and self._exchange):
            await self.connect()

        if not self.__channel:
            self._logger.error("Failed to establish connection, cannot send message")
            return

        try:
            queue = await self.__channel.declare_queue(name=worker, durable=True)
            await queue.bind(self._exchange, routing_key=worker)

            message = Message(
                body=json.dumps(task_payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=2
            )

            await self._exchange.publish(message, routing_key=worker)

        except Exception as e:
            self._logger.error(f"Failed to send task: {e}")
            try:
                await self.__channel.close()
            except Exception:
                pass
            self.__channel = None

    async def close(self):
        if self.__connection:
            await self.__connection.close()
            self.__connection = None
            self.__channel = None
            self._exchange = None
