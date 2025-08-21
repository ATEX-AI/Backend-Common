import logging

from fastapi import FastAPI
from redis import asyncio as redis


def create_redis_pool(
    connection_url,
    logger: logging.Logger,
) -> redis.Redis:  # TODO - rename
    try:
        pool = redis.ConnectionPool.from_url(connection_url)
        return redis.Redis(connection_pool=pool)
    except Exception as e:
        logger.warning(f"An error occurred when trying to create a new pool: {e}")
        raise


def get_redis_pool(app: FastAPI) -> redis.Redis:
    pool = getattr(app.state, "redis_websocket_pool", None)

    if pool is None:
        raise RuntimeError("Redis Pool does not found in app.state")

    return pool
