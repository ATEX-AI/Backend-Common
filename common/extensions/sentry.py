import logging
import os

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.modules import ModulesIntegration

try:
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    _has_sqlalchemy = True
except Exception:
    _has_sqlalchemy = False


sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,
)

# Transient errors that are expected during deployments / service restarts.
# These are handled by reconnection logic and should not create Sentry issues.
_IGNORED_ERROR_SUBSTRINGS = [
    "Connection.Close(reply_code=",       # RabbitMQ expected reconnection
    "Unexpected connection close from remote",  # aio_pika reconnect event
    "ConnectionResetError",               # TCP reset during restart
    "> closed",                           # aio_pika Connection object closed
    "TelegramNetworkError",               # Telegram API transient network issues
    "Connection reset by peer",           # TCP reset from external APIs
    "Task was destroyed but it is pending",  # asyncio task cleanup on shutdown
]

# PII/secret field names that should be redacted before sending to Sentry.
# Defense-in-depth: even with send_default_pii=False, request bodies and
# breadcrumb data can leak customer phone numbers, emails, chat messages, etc.
_PII_FIELD_NAMES = frozenset({
    "phone", "phone_number", "email", "first_name", "last_name", "full_name",
    "password", "token", "access_token", "refresh_token", "api_key", "secret",
    "message", "message_text", "text", "chat_content", "body",
})


def _scrub_pii(data):
    """Recursively scrub known PII/secret fields from dict/list payloads."""
    if isinstance(data, dict):
        return {
            k: ("[Filtered]" if str(k).lower() in _PII_FIELD_NAMES else _scrub_pii(v))
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_scrub_pii(v) for v in data]
    return data


def _before_send(event, hint):
    """Filter out known transient/expected errors + scrub PII from Sentry payloads."""
    message = (event.get("logentry") or {}).get("message", "")
    if not message:
        message = event.get("message", "")

    for pattern in _IGNORED_ERROR_SUBSTRINGS:
        if pattern in message:
            return None

    # Also check exception values
    exceptions = (event.get("exception") or {}).get("values", [])
    for exc in exceptions:
        exc_value = exc.get("value", "")
        for pattern in _IGNORED_ERROR_SUBSTRINGS:
            if pattern in exc_value:
                return None

    # PII scrubbing (GDPR defense-in-depth)
    request = event.get("request") or {}
    if isinstance(request.get("data"), (dict, list)):
        request["data"] = _scrub_pii(request["data"])
    if isinstance(request.get("query_string"), (dict, list)):
        request["query_string"] = _scrub_pii(request["query_string"])

    breadcrumbs = (event.get("breadcrumbs") or {}).get("values") or []
    for crumb in breadcrumbs:
        if isinstance(crumb.get("data"), (dict, list)):
            crumb["data"] = _scrub_pii(crumb["data"])

    return event


def configure_sentry(sentry_dsn_url, logger: logging.Logger = None):
    if logger:
        logger.debug("Configuring sentry...")
    environment = os.getenv("SENTRY_ENVIRONMENT", "development")
    integrations = [
        AioHttpIntegration(),
        AtexitIntegration(),
        DedupeIntegration(),
        ExcepthookIntegration(),
        ModulesIntegration(),
        StdlibIntegration(),
        sentry_logging,
    ]
    if _has_sqlalchemy:
        integrations.append(SqlalchemyIntegration())
    sentry_sdk.init(
        dsn=sentry_dsn_url,
        environment=environment,
        integrations=integrations,
        traces_sample_rate=0.2,
        profiles_sample_rate=0.1,
        send_default_pii=False,
        enable_tracing=True,
        auto_enabling_integrations=False,
        before_send=_before_send,
    )
