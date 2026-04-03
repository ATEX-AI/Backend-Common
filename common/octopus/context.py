import json
import logging
import redis

logger = logging.getLogger("octopus.context")


class OctopusContext:
    """Read aggregated context from Redis hash. One call = full company context."""

    FIELDS = [
        "last_chats", "last_leads", "last_content", "kb_changes",
        "crm_snapshot", "team_activity", "project_tasks",
        "system_health", "utm_clicks_24h",
    ]

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
            except Exception:
                return None
        return self._client

    def get(self, company_id: int) -> dict:
        """Get full Octopus context for a company. Returns {} on any failure."""
        try:
            client = self._get_client()
            if not client:
                return {}
            key = f"octopus:context:{company_id}"
            raw = client.hgetall(key)
            if not raw:
                return {}
            result = {}
            for field_name, value in raw.items():
                try:
                    result[field_name] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field_name] = value
            return result
        except Exception as exc:
            logger.warning("Octopus: context read failed for company %s: %s", company_id, exc)
            self._client = None
            return {}

    def set_field(self, company_id: int, field: str, value, ttl: int = 3600) -> bool:
        """Update a single context field. Used by the consumer."""
        try:
            client = self._get_client()
            if not client:
                return False
            key = f"octopus:context:{company_id}"
            client.hset(key, field, json.dumps(value, ensure_ascii=False, default=str))
            client.expire(key, ttl)
            return True
        except Exception as exc:
            logger.warning("Octopus: set_field failed: %s", exc)
            self._client = None
            return False
