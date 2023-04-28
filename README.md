# django-utils
A collection of utils used in our Django based web applications

[Changelog](CHANGELOG.md)

## Development

Installing dependencies, assuming you have poetry installed:

``` bash
poetry install
```

## Release

This package uses towncrier to manage the changelog, and to introduce new changes, a file with a concise title and a brief explanation of what the change accomplishes should be created in the `changes` directory, with a suffix indicating whether the change is a feature, bugfix, or other.

To make a release and publish it to PyPI, the following command can be executed:

``` bash
./bin/release
```

This script utilizes zest.releaser and towncrier to create the release, build the wheel, and publish it to PyPI.

Before running the release command, it is necessary to configure poetry with an access token for PyPI by executing the following command and inserting the token stored in 1password:

``` bash
poetry config pypi-token.pypi <token>
```

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
* `SENTRY_TAGS` (default: `{}`)

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

Creates a snapshot of the media root folder, resets the database, restores permissions and loads initial data (calls `python manage.py load_e2e_data --datasets initial`).

#### E2ETestTearDownView (`/teardown`)

Cleans up the media root folder.

#### TestingLoginView (`/login`)

Authenticates a user when posting a JSON request body such as `{"username": "username", "password": "password"}`.

#### E2ETestLoadDataView (`/load_data`)

Loads given datasets using `python manage.py load_e2e_data --datasets [datasets]` when posting a JSON request body such as `{"datasets": ["initial"]}`.

#### PingView (`/ping`)

Responds an HTTP response with status code 200.


## Protected File View

Django Utils offers a way to protect your files from anonymous access.

### Requirements

The file view relies on `django-sendfile2` and `djangorestframework`.

```bash
pip install django-sendfile2
pip install djangorestframework
```

### View

Django Utils offers a file getter view under `django_utils.views.FileGetterView`.
This view has to be used for a protected access to files.
The view will only deliver the files requested, when the user is logged in by default.
In order to override the behavior, subclass the `FileGetterView` and implement `get_object`.
The view will only permit access, when the `get_object` method evaluates a model instance. Simply return `None` to block the access.

```python
from django_utils.views import FileGetterView

class MyFileView(FileGetterView):
    def get_object(self, model_class, id, request, **kwargs):
        return model_class._default_manager.get(user=request.user, id=id)
```

### URL

To relay all the requests for assets to the file getter view, append your urls with a pattern like this:

```python
urlpatterns = [
    re_path(r"media/(?P<file_info>.*)", FileGetterView.as_view(), name="media"),
]
```

Your pattern has to end with `(?P<file_info>.*)` and register a file getter view.

### Serializer

In order for the file getter view to resolve certain model fields, the field must be a `ProtectedImageField` in the serializer:

```python
from django_utils.serializer.fields import ProtectedImageField

class MySerializer(Serializer):
    image = ProtectedImageField()

    class Meta:
        fields = (
            "image",
        )
```

### Settings

Configure your settings as follows:

```python
SENDFILE_BACKEND = "django_sendfile.backends.simple"
SENDFILE_ROOT = self.BASE_DIR / "media"
MEDIA_URL = "/media/"
```

The `SENDFILE_ROOT` has to point to the directory where your files will be stored.
The `MEDIA_URL` has to match the url pattern.

If you use uwsgi in production, apply the following settings to your `uwsgi.ini`:

```ini
plugins = router_static
static-safe = %(base_path)/media
collect-header = X-Sendfile X_SENDFILE
response-route-if-not = empty:${X_SENDFILE} static:${X_SENDFILE}
```

Make sure the `static-safe` matches your `MEDIA_URL` setting.

### Caching

The object the file is attached to, must have a field named `modified`, that changes every time the object is updated, in order to create a new URL when the file is updated.
The field is not mandatory but required for the caching to work properly.


## Authentication

### SessionAuthentication

Based on ``SessionAuthentication`` of Django REST Framework, this class allows distinguishing status codes 401 and 403 in API responses.
It returns a response with status code 401 for unauthenticated requests (user is not logged in) and returns a response with status code 403 if the user is logged in but does not have sufficient permissions.

Requires ``djangorestframework``.

Usage:

```python
# myproject/settings/base.py

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["django_utils.authentication.SessionAuthentication"],
}
```

## Delete hooks

Ianus is capable of requesting user deletion and notifying when users have been deleted. To enable this feature, Ianus requires certain views to be present in the service. Django Utils provides a default implementation for these views, which handle token authentication and validation of the request made by Ianus. To register these views, add the urlpatterns in your service being notified by Ianus, as shown below:

``` python
# urls.py
from django.urls import include

urlpatterns = [
    path("", include("django_utils.webhooks.delete_user.urls")),
]
```

When Ianus requests an inquiry to delete a user, a hook is called to determine if the user can be deleted or not. The default hook will always accept the inquiry. However, this behavior can be overridden by providing a module with an `inquire_delete` method. To do this, configure the `IANUS_USER_DELETE_HOOKS` setting and point it to a module that implements the `inquire_delete` method, as shown below:

``` python
# settings.py
IANUS_USER_DELETE_HOOKS = "backend.authentication.delete_hooks"
```

The `inquire_delete` method will receive the user that Ianus is inquiring to delete as a parameter. The `inquire_delete` method must return a tuple, where the first component is a boolean indicating whether the inquiry has passed or not, and the second component is a reason as a string, which tells Ianus the reason behind a failing inquiry. When the inquiry is successful, the reason can be set to `None`, as shown below:

``` python
# delete_hooks.py
def inquire_delete(user):
    return (True, None)
```

Alternatively, you can return a failure message to Ianus, indicating why the inquiry failed, as shown below:

``` python
# delete_hooks.py
def inquire_delete(user):
    return (False, "User cannot be deleted due to specific reasons.")
```

The same concept applies to user delete notification. A method with the name `subscribe_delete` in the same module has to be provided to subscribe to user deletion from Ianus. The `subscribe_delete` method will receive the user that was deleted in Ianus as an argument. The default implementation will always delete the user. You can provide your own implementation in this method, as shown below:

``` python
# delete_hooks.py
def subscribe_delete(user):
    user.delete()
```

To configure the authentication token for the delete hook API, use the `IANUS_DELETE_HOOK_API_TOKEN` setting. The authentication token that is configured in Ianus must match this token for the authentication to work correctly.
