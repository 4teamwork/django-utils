# django-utils
A collection of utils used in our Django based web applications


## Settings

### LogMixin

A mixin containing the logging configuration with default values suited for production.

Available environment variables:

* `LOGGING_LEVEL` (default: `"WARNING"`)
* `LOGGING_HANDLERS` (default: `["stream"]`)

Usage:

````python
# myproject/settings/production.py

from django_utils.settings.logging import LogMixin

from myproject.settings.base import Base

class Production(LogMixin, Base):
    pass
````

### SentryMixin

A mixin to report errors to Sentry.

Available environment variables:

* `SENTRY_DSN` (required)
* `SENTRY_ENVIRONMENT` (default: `"Production"`)
* `SENTRY_CACERTS` (default: `None`)

Usage:

````python
# myproject/settings/production.py

from django_utils.settings.sentry import SentryMixin

from myproject.settings.base import Base

class Production(SentryMixin, Base):
    pass
````


## Management Commands

ℹ️ In order to use the management commands, you need to add `django_utils` to the `INSTALLED_APPS` setting. 

### sentry_test

Use this command to test the connection to Sentry. The command raises an exception on purpose. This should be reported in Sentry.

Usage:

```bash
python manage.py sentry_test
```


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
