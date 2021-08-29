from django import forms
from django.db import models


class TextField(models.TextField):
    """
    A TextField (without max_length) which displays its form element as a single-line 'CharField'
    with extended width in the Django admin.
    """

    def formfield(self, **kwargs):
        formfield = super().formfield(**kwargs)
        if hasattr(formfield, "choices"):
            # Use the original widget (select) if choices are available.
            return formfield
        formfield.widget = forms.TextInput(attrs={"style": "width: 30em;"})
        return formfield
