# django-utils
A collection of utils used in our Django based web applications

## Model Fields

### TextField

A TextField (without max_length) which displays its form element as a single-line 'CharField' with extended width in the Django admin.

Usage:

```python
# models.py

from django.db import models
from django_utils.db.fields import TextField


class MyModel(models.Model):
    TextField(verbose_name="My TextField")
```
