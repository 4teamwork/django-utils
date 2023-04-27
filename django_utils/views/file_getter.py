import base64
from urllib import parse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.views.generic import View
from django_sendfile import sendfile


class FileGetterView(LoginRequiredMixin, View):
    """
    This view will deliver all the files and check if the user is logged in. As the whole application is only
    available privately, we also need to protect our user generated content (images etc.)
    """

    http_method_names = ["get"]

    def get(self, request, file_info):
        obj, file = self.get_object_from_url(request, file_info)
        if not obj:
            raise Http404
        return sendfile(request, file.path)

    def get_object_from_url(self, request, url):
        """
        Resolve objects based on urls provided by "get_url_for_object".
        If any of this fails, a 404 should be raised in the view, but logging information for developers must be available.
        """
        try:
            (app, model, id, field, hash) = base64.urlsafe_b64decode(parse.unquote(url)).decode().split("|")
            model = ContentType.objects.get(app_label=app, model=model)
            obj = self.get_object(model.model_class(), id, request=request, field=field)
            return obj, getattr(obj, field)
        except Exception:
            return None, None

    def get_object(self, model_class, id, **kwargs):
        return model_class._default_manager.get(id=id)
