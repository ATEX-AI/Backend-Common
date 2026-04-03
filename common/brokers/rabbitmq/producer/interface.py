import json
import asyncio
import logging

from aio_pika import ExchangeType, Message

from common.brokers.rabbitmq.connection_pool import ConnectionPool


class ProducerBasicInterface:
    def __init__(self, broker_host_url: str, logger: logging.Logger):
        self._broker_host_url = broker_host_url
        self.__channel = None
        self._exchange = None
        self._logger = logger
        self._lock = asyncio.Lock()

    @property
    def has_connection(self) -> bool:
        return self.__channel is not None and not self.__channel.is_closed

    @property
    def has_channel(self) -> bool:
        return self.__channel is not None and not self.__channel.is_closed

    async def connect(self) -> None:
        async with self._lock:
            if self.has_channel and self._exchange:
                return

            # Close stale channel if any
            if self.__channel:
                try:
                    await self.__channel.close()
                except Exception:
                    pass
                self.__channel = None
                self._exchange = None

            try:
                pool = await ConnectionPool.get_instance(self._broker_host_url)
                self.__channel = await pool.acquire_channel()
                self._exchange = await self.__channel.declare_exchange(
                    "DirectExchange", ExchangeType.DIRECT, durable=True
                )
            except Exception as e:
                self._logger.warning(f"Error during {self._broker_host_url} connection: {e}")
                self.__channel = None
                self._exchange = None

    async def send_task(self, worker: str, task_payload: dict):
        if not (self.has_channel and self._exchange):
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
            self._exchange = None

    async def close(self):
        """Close this producer's channel. Does NOT close the shared connection."""
        if self.__channel and not self.__channel.is_closed:
            try:
                await self.__channel.close()
            except Exception:
                pass
        self.__channel = None
        self._exchange = None
