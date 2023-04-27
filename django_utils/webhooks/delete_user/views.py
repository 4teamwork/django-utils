import importlib

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

from django_utils.webhooks.delete_user import default_delete_hooks
from django_utils.webhooks.delete_user.serializers import InquireDeleteUserSerializer
from django_utils.webhooks.delete_user.serializers import SubscribeUserDeleteSerializer
from django_utils.webhooks.delete_user.token_authentication import WebhookTokenAuthentication


User = get_user_model()


try:
    delete_hooks = importlib.import_module(settings.IANUS_USER_DELETE_HOOKS)
except ModuleNotFoundError:
    delete_hooks = default_delete_hooks


class InquireDeleteView(APIView):
    authentication_classes = [WebhookTokenAuthentication]

    def post(self, request, format=None):
        serializer = InquireDeleteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(username=serializer.validated_data["userid"])
            passed, reason = delete_hooks.inquire_delete(user)
            if not passed:
                return Response(data={"reason": reason}, status=412)
            return Response(status=204)
        except User.DoesNotExist:
            return Response(status=204)


class SubscribeDeleteView(APIView):
    authentication_classes = [WebhookTokenAuthentication]

    def post(self, request, format=None):
        serializer = SubscribeUserDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(username=serializer.validated_data["userid"])
            delete_hooks.subscribe_delete(user)
            return Response(status=204)
        except User.DoesNotExist:
            return Response(status=204)
