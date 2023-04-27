import json
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.core.management import call_command
from django.db import connection
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django_utils.testing.filestructure import cleanup_path
from django_utils.testing.filestructure import filestructure_snapshot


logger = logging.getLogger(__name__)

SNAPSHOT_BEFORE = []


@method_decorator(csrf_exempt, name="dispatch")
class E2ETestSetupView(View):
    def reset_database(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DO
                $func$
                BEGIN
                EXECUTE
                (SELECT 'TRUNCATE TABLE ' || string_agg(oid::regclass::text, ', ') || ' RESTART IDENTITY'
                    FROM   pg_class
                    WHERE  relkind = 'r'  -- only tables
                    AND    relnamespace = 'public'::regnamespace
                );
                END
                $func$;
                """
            )

    def clear_solr(self):
        haystack_connections = getattr(settings, "HAYSTACK_CONNECTIONS", {})
        if not haystack_connections:
            return
        default_engine = haystack_connections.get("default", {}).get("ENGINE", "")
        if default_engine != "haystack.backends.solr_backend.SolrEngine":
            return
        call_command("clear_index", "--noinput")

    def load_initial_data(self):
        call_command("load_e2e_data", datasets=["initial"])

    def restore_permissions(self):
        """
        Restore permissions using a management command provided by django-extensions.
        """
        call_command("update_permissions")

    def post(self, request, *args, **kwargs):
        logger.info("E2E test setup")

        # Create a snapshot of the media root folder before the test
        SNAPSHOT_BEFORE.extend(filestructure_snapshot(settings.MEDIA_ROOT))

        self.reset_database()
        self.clear_solr()
        self.restore_permissions()
        self.load_initial_data()

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class E2ETestTearDownView(View):
    def post(self, request, *args, **kwargs):
        logger.info("E2E test teardown")

        # Cleanup the media root folder by removing any files added since the snapshot in the
        # `E2ETestSetupView`.
        cleanup_path(settings.MEDIA_ROOT, SNAPSHOT_BEFORE)
        SNAPSHOT_BEFORE.clear()

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class TestingLoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get("username", "username")
        password = data.get("password", "password")
        user = authenticate(request, username=username, password=password)
        if user and user.is_authenticated:
            login(request, user)
            return HttpResponse(status=200)
        return HttpResponse(status=401)


@method_decorator(csrf_exempt, name="dispatch")
class E2ETestLoadDataView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        datasets = data.get("datasets")
        logger.info(f"E2E loading datasets {datasets}")
        call_command("load_e2e_data", datasets=datasets)
        return HttpResponse(status=200)


class PingView(View):
    def head(self, request, *args, **kwargs):
        return HttpResponse("pong", status=200)
