import logging
import redis

logger = logging.getLogger("octopus.publisher")


class OctopusPublisher:
    """Fire-and-forget event publisher. NEVER raises exceptions to callers."""

    def __init__(self, redis_url: str = "", redis_db: int = 1):
        self._redis_url = redis_url
        self._redis_db = redis_db
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                self._client = redis.Redis.from_url(
                    self._redis_url, db=self._redis_db, decode_responses=True,
                    socket_connect_timeout=2, socket_timeout=2,
                )
            except Exception as exc:
                logger.warning("Octopus: Redis connection failed: %s", exc)
                return None
        return self._client

    def emit(self, event) -> bool:
        """Publish event to Redis stream. Returns True on success, False on failure."""
        try:
            client = self._get_client()
            if not client:
                return False
            stream_key = f"octopus:events:{event.company_id}"
            client.xadd(stream_key, {"event": event.to_json()}, maxlen=500)
            return True
        except Exception as exc:
            logger.warning("Octopus: emit failed for %s: %s", event.type, exc)
            self._client = None  # Reset on failure
            return False
