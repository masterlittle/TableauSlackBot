import logging

import sentry_sdk

from app.config import Settings

config = Settings()


def log_exception(exception: Exception, message=None):
    if message:
        logging.exception(message)
    else:
        logging.exception(exception)
    if config.SENTRY_DSN:
        sentry_sdk.capture_exception(exception)


def log_error(exception, message=None):
    if message:
        logging.error(message)
    else:
        logging.error(exception)
    if config.SENTRY_DSN:
        sentry_sdk.capture_exception(exception)