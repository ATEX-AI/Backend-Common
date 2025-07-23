import logging

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


def configure_sentry(sentry_sdn_url, logger: logging.Logger):
    logger.debug("Configuring sentry...")
    sentry_sdk.init(
        dsn=sentry_sdn_url,
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
        # environment=ENV,
        auto_enabling_integrations=False,
    )
