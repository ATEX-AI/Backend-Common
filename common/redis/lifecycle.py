import logging

from fastapi import FastAPI

from common.redis.core import create_redis_pool


async def on_redis_startup(app: FastAPI, connection_url, logger: logging.Logger):
    redis_pool = create_redis_pool(connection_url=connection_url, logger=logger)

    app.state.redis_pool = redis_pool

    logger.info(f"Redis pool created successfully.")


async def on_redis_shutdown(app: FastAPI, logger: logging.Logger):
    pool_to_close = getattr(app.state, "redis_pool", None)

    if pool_to_close:
        logger.info("Clothing Redis pool...")
        await pool_to_close.close()
        logger.info("Redis pool is closed.")
