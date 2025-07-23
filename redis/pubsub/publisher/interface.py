from typing import Any

from redis.asyncio import Redis

from redis.pubsub import BaseEventType, EventPayload


class EventPublisher:

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def publish(
        self,
        channel: str,
        event_cls: EventPayload,
        event: BaseEventType,
        data: Any,
        **kwargs,
    ) -> None:
        payload = event_cls(event=event, data=data, **kwargs).model_dump_json()
        await self._redis.publish(channel, payload)

    async def publish_payload(self, *, channel: str, payload: EventPayload) -> None:
        await self._redis.publish(channel, payload.model_dump_json())
