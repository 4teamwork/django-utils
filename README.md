# django-utils
A collection of utils used in our Django based web applications


## Settings

### LogMixin

A mixin containing the logging configuration with default values suited for production.

Available environment variables:

* `LOGGING_LEVEL` (default: `"WARNING"`)
* `LOGGING_HANDLERS` (default: `["stream"]`)
* `LOGGING_FILENAME` (default: `<settings.BASE_DIR>/log/django.log`)

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


## Testing

### Views

This package provides views which can be used in E2E tests for test setup and teardown and to login or create test data.

ℹ️ These views rely on the availability of a management command executable as `python manage.py load_e2e_data --datasets initial` to load initial fixture data for the tests. 

⚠️ Important: Never add these views (through `django_utils.testing.urls`) in production mode! They should only be used for testing purposes.

Usage:

```python
# myproject/settings/testing.py

from django_utils.settings.logging import LogMixin

from myproject.settings.base import Base

class TestingE2E(LogMixin, Base):
    LOGGING_LEVEL = "INFO"
    LOGGING_HANDLERS = ["file"]

    @property
    def LOGGING_FILENAME(self):
        return super().BASE_DIR / "log" / "e2e.log"


# myproject/urls.py

from django.conf import settings
from django.urls import include
from django.urls import path

urlpatterns = [
    # ...
]

if settings.CONFIGURATION == "settings.TestingE2E":
    urlpatterns += [
        path("e2e/", include("django_utils.testing.urls")),
    ]
```

#### E2ETestSetupView (`/setup`)

Creates a snapshot of the media root folder, resets the database and loads initial data (calls `python manage.py load_e2e_data --datasets initial`). 

#### E2ETestTearDownView (`/teardown`)

Cleans up the media root folder.

#### TestingLoginView (`/login`)

Authenticates a user when posting a JSON request body such as `{"username": "username", "password": "password"}`.

#### E2ETestLoadDataView (`/load_data`)

Loads given datasets using `python manage.py load_e2e_data --datasets [datasets]` when posting a JSON request body such as `{"datasets": ["initial"]}`.

#### PingView (`/ping`)

Responds an HTTP response with status code 200.
