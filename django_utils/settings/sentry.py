import sentry_sdk
from configurations import values
from sentry_sdk.integrations.django import DjangoIntegration


class SentryMixin:
    SENTRY_DSN = values.Value(environ_required=True, environ_prefix="")

    # A path to an alternative CA bundle file in PEM-format.
    SENTRY_CACERTS = values.Value(None, environ_prefix="")

    SENTRY_TAGS = values.DictValue(default={}, environ_prefix="")
    SENTRY_ENVIRONMENT = values.Value("Production", environ_prefix="")
    SENTRY_SERVER_NAME = values.Value(None, environ_prefix="")
    SENTRY_IN_APP_INLCUDE = values.ListValue(default=[], environ_prefix="")
    SENTRY_IN_APP_EXCLUDE = values.ListValue(default=[], environ_prefix="")

    @classmethod
    def post_setup(cls):
        super().post_setup()
        cls.init_sentry_sdk()
        cls.configure_sentry_tags()

    @classmethod
    def init_sentry_sdk(cls):
        if cls.SENTRY_DSN is None:
            return

        sentry_sdk.init(**cls.make_sentry_init_kwargs())

    @classmethod
    def make_sentry_init_kwargs(cls):
        return dict(
            dsn=cls.SENTRY_DSN,
            integrations=[DjangoIntegration()],
            send_default_pii=True,
            environment=cls.get_sentry_environment(),
            ca_certs=cls.SENTRY_CACERTS,
            release=cls.get_sentry_release_version(),
            server_name=cls.SENTRY_SERVER_NAME,
            in_app_include=cls.SENTRY_IN_APP_INLCUDE,
            in_app_exclude=cls.SENTRY_IN_APP_EXCLUDE,
        )

    @classmethod
    def get_sentry_environment(cls):
        return cls.SENTRY_ENVIRONMENT

    @classmethod
    def get_sentry_release_version(cls):
        return None

    @classmethod
    def get_sentry_tags(cls):
        return cls.SENTRY_TAGS

    @classmethod
    def configure_sentry_tags(cls):
        if cls.SENTRY_DSN is None:
            return

        for tagname, tagvalue in cls.get_sentry_tags().items():
            sentry_sdk.set_tag(tagname, tagvalue)
