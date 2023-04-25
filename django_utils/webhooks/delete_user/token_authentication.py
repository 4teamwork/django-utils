from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class WebhookTokenUser:
    """
    We don't want to attach the token to a specific user, but the Authentication class needs to return a user-like
    object (e.g. which has an "is_authenticated" method).
    """

    @property
    def is_simple_token_dummy(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_superuser(self):
        return False

    def has_perm(self, *args, **kwargs):
        """
        This "user" does not have any special permissions.
        """
        return False


class WebhookTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        if not settings.IANUS_DELETE_HOOK_API_TOKEN:
            raise exceptions.AuthenticationFailed("No token set on server.")

        if key != settings.IANUS_DELETE_HOOK_API_TOKEN:
            raise exceptions.AuthenticationFailed("Invalid token.")
        return WebhookTokenUser(), None
