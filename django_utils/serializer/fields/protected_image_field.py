from django.urls import reverse
from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType
import base64
from urllib import parse


class ProtectedImageField(serializers.ImageField):
    def get_url_for_object(self, obj, field_name):
        """
        Create a string with all information required to access the object, in the form of
        <app_label>|<model>|<pk>|<field_name>
        """
        content_type = ContentType.objects.get_for_model(obj)
        return parse.quote_plus(
            base64.urlsafe_b64encode(
                "|".join([content_type.app_label, content_type.model, str(obj.pk), field_name]).encode()
            )
        )

    def to_representation(self, value):
        return reverse("media", kwargs={"file_info": self.get_url_for_object(value.instance, self.field_name)})
