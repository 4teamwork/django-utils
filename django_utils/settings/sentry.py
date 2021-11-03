import sentry_sdk
from configurations import values
from sentry_sdk.integrations.django import DjangoIntegration


class SentryMixin:
    SENTRY_DSN = values.Value(environ_required=True, environ_prefix="")

    SENTRY_ENVIRONMENT = values.Value("Production", environ_prefix="")

    # A path to an alternative CA bundle file in PEM-format.
    SENTRY_CACERTS = values.Value(None, environ_prefix="")

    SENTRY_TAGS = values.DictValue(default={}, environ_prefix="")

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
