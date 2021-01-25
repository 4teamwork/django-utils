import sys

import sentry_sdk
from configurations import values
from sentry_sdk.integrations.django import DjangoIntegration


class LogMixin:
    """
    This mixins contains the logging configuration of our Django based
    web applications. Its default values are suited for production.
    """

    LOGGING_LEVEL = values.Value("WARNING")

    LOGGING_HANDLERS = values.ListValue(["stream"])

    LOGGING_STREAM = sys.stderr

    @property
    def LOGGING(self):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "{asctime} {levelname} {name} {message}",
                    "style": "{",
                },
                "simple": {
                    "format": "{message}",
                    "style": "{",
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                    "stream": self.LOGGING_STREAM,
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "formatter": "verbose",
                    "filename": super().BASE_DIR / "log" / "django.log",
                },
                "stream": {
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                },
            },
            "loggers": {
                "": {
                    "handlers": self.LOGGING_HANDLERS,
                    "level": self.LOGGING_LEVEL,
                },
                "django": {
                    "handlers": self.LOGGING_HANDLERS,
                    "level": self.LOGGING_LEVEL,
                    "propagate": False,
                },
                "django.db": {
                    "handlers": self.LOGGING_HANDLERS,
                    "level": self.LOGGING_LEVEL,
                    "propagate": False,
                },
            },
        }


class SentryMixin:
    SENTRY_DSN = values.Value(environ_required=True, environ_prefix="")

    SENTRY_ENVIRONMENT = values.Value("Production", environ_prefix="")

    # A path to an alternative CA bundle file in PEM-format.
    SENTRY_CACERTS = values.Value(None, environ_prefix="")

    SENTRY_TAGS = {}

    @classmethod
    def post_setup(cls):
        super().post_setup()
        if cls.SENTRY_DSN is not None:
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                integrations=[DjangoIntegration()],
                send_default_pii=True,
                environment=cls.SENTRY_ENVIRONMENT,
                ca_certs=cls.SENTRY_CACERTS,
            )

        if cls.SENTRY_TAGS:
            for tagname, tagvalue in cls.SENTRY_TAGS.items():
                sentry_sdk.set_tag(tagname, tagvalue)
