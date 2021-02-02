from django.core.management import BaseCommand
from sentry_sdk import capture_exception


class SentryTestException(Exception):
    pass


def bad():
    raise SentryTestException()


class Command(BaseCommand):
    """
    Use this command to test the connection to Sentry. The command raises an
    exception on purpose. This should be reported in Sentry. You may immediately
    resolve the issue in Sentry then.
    """

    def handle(self, *args, **options):
        # Manually generate a Sentry event as per https://docs.sentry.io/platforms/python/guides/django/#verify
        try:
            bad()
        except Exception as e:
            capture_exception(e)
