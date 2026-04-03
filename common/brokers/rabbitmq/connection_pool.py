"""
Singleton AMQP connection pool.

Instead of each consumer/producer opening its own TCP connection to RabbitMQ,
all components within one process share a single robust connection.
Channels are cheap and multiplexed over that one connection.

Usage:
    pool = ConnectionPool.get_instance(broker_host_url)
    channel = await pool.acquire_channel()
    # ... use channel ...
    await pool.release_channel(channel)
"""

import asyncio
import logging

from aio_pika import connect_robust, Connection, Channel

logger = logging.getLogger(__name__)


class ConnectionPool:
    """
    Per-URL singleton that holds one robust AMQP connection.

    Thread-safety: NOT thread-safe. Designed for use within a single
    asyncio event loop (one per process in the bots-service architecture).
    """

    _instances: dict[str, "ConnectionPool"] = {}
    _class_lock = asyncio.Lock()

    def __init__(self, broker_host_url: str) -> None:
        self._broker_host_url = broker_host_url
        self._connection: Connection | None = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Singleton accessor
    # ------------------------------------------------------------------

    @classmethod
    async def get_instance(cls, broker_host_url: str) -> "ConnectionPool":
        """
        Return the singleton pool for the given URL.

        Because each seeder worker runs in its own process with its own
        event loop, the class-level dict is process-local -- no cross-process
        sharing issues.
        """
        # Fast path (no lock)
        pool = cls._instances.get(broker_host_url)
        if pool is not None:
            return pool

        # Slow path (with lock for first-time creation)
        async with cls._class_lock:
            pool = cls._instances.get(broker_host_url)
            if pool is not None:
                return pool
            pool = cls(broker_host_url)
            cls._instances[broker_host_url] = pool
            return pool

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    async def _ensure_connection(self) -> Connection:
        """Return the shared connection, creating it if needed."""
        async with self._lock:
            if self._connection is not None and not self._connection.is_closed:
                return self._connection

            logger.info(
                "ConnectionPool: opening shared AMQP connection to %s",
                self._broker_host_url,
            )
            self._connection = await connect_robust(self._broker_host_url)
            return self._connection

    async def acquire_channel(self, prefetch_count: int | None = None) -> Channel:
        """
        Open a new channel on the shared connection.

        Channels are lightweight (just a number on the existing TCP socket).
        Each consumer / producer should hold its own channel.
        """
        connection = await self._ensure_connection()
        channel = await connection.channel()
        if prefetch_count is not None:
            await channel.set_qos(prefetch_count=prefetch_count)
        return channel

    @staticmethod
    async def release_channel(channel: Channel) -> None:
        """Close a channel (best-effort)."""
        if channel and not channel.is_closed:
            try:
                await channel.close()
            except Exception:
                pass

    async def close(self) -> None:
        """Tear down the shared connection (called on process shutdown)."""
        async with self._lock:
            if self._connection and not self._connection.is_closed:
                try:
                    await self._connection.close()
                except Exception:
                    pass
            self._connection = None

    @classmethod
    async def close_all(cls) -> None:
        """Shut down every pool (useful in atexit / signal handlers)."""
        for pool in cls._instances.values():
            await pool.close()
        cls._instances.clear()
