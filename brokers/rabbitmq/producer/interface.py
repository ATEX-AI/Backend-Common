import json
import asyncio
import logging

from aio_pika import connect_robust, ExchangeType, Message


class ProducerBasicInterface:
    def __init__(self, broker_host_url: str, logger: logging.Logger):
        self._broker_host_url = broker_host_url
        self.__connection = None
        self.__channel = None
        self._logger = logger

    @property
    def has_connection(self) -> bool:
        return self.__connection is not None and not self.__connection.is_closed

    @property
    def has_channel(self) -> bool:
        return self.__channel is not None and not self.__channel.is_closed

    async def connect(self) -> None:
        if self.has_connection and self.has_channel:
            return
        
        try:
            await self.close()

        except Exception as e:
            self._logger.exception(f"Error during closing {self._broker_host_url} connection: {e}")

        retry_delay = 2
        while not self.has_connection and not self.has_channel:
            try:
                self.__connection = await connect_robust(self._broker_host_url)
                self.__channel = await self.__connection.channel()

            except Exception as e:
                self._logger.exception(f"Error during {self._broker_host_url} connection: {e}")
                await asyncio.sleep(retry_delay)

    async def send_task(self, worker: str, task_payload: dict):
        if not (self.has_connection and self.has_channel):
            await self.connect()
        else:
            if self.__channel and not self.__channel.is_closed:
                await self.__channel.close()

        self.__channel = await self.__connection.channel()

        exchange = await self.__channel.declare_exchange(
            "DirectExchange", ExchangeType.DIRECT
        )
        queue = await self.__channel.declare_queue(name=worker, durable=True)
        await queue.bind(exchange, routing_key=worker)

        message = Message(
            body=json.dumps(task_payload).encode("utf-8"),
            content_type="application/json",
        )

        await exchange.publish(message, routing_key=worker)

    async def close(self):
        if self.__connection:
            await self.__connection.close()

        if self.__channel:
            await self.__channel.close()
