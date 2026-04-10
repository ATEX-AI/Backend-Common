import logging
import os

import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.modules import ModulesIntegration


sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,
)


def configure_sentry(sentry_dsn_url, logger: logging.Logger = None):
    if logger:
        logger.debug("Configuring sentry...")
    environment = os.getenv("SENTRY_ENVIRONMENT", "development")
    sentry_sdk.init(
        dsn=sentry_dsn_url,
        environment=environment,
        integrations=[
            AioHttpIntegration(),
            AtexitIntegration(),
            DedupeIntegration(),
            ExcepthookIntegration(),
            ModulesIntegration(),
            SqlalchemyIntegration(),
            StdlibIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=0.2,
        profiles_sample_rate=0.1,
        send_default_pii=False,
        enable_tracing=True,
        auto_enabling_integrations=False,
    )
