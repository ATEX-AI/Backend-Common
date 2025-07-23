import logging
from fastapi import FastAPI
from redis.asyncio import Redis
from common.redis.pubsub import EventSubscriber, BaseEventType, EventPayload


async def on_pubsub_startup(
    app: FastAPI,
    events_subscriber: EventSubscriber,
    events_cls: BaseEventType,
    events_payload_cls: EventPayload,
    logger: logging.Logger,
):
    redis = getattr(app.state, "redis_pool", None)
    events_subscriber: EventSubscriber = events_subscriber(
        redis,
        logger=logger,
        events_cls=events_cls,
        events_payload_cls=events_payload_cls,
    )
    await events_subscriber.start()
    app.state.events_subscriber = events_subscriber


async def on_pubsub_shutdown(
    app: FastAPI,
) -> None:
    events_subscriber: EventSubscriber | None = getattr(
        app.state, "events_subscriber", None
    )
    if events_subscriber:
        await events_subscriber.stop()
