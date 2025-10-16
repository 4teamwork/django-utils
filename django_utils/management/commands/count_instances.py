import json
from typing import Any
from typing import Callable

from django.apps import apps
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser
from django.db.models import Model


class Command(BaseCommand):
    help = (
        "Counts instances for each model.\n"
        "Example usages:\n"
        "  python manage.py count_instances\n"
        "  python manage.py count_instances --apps backend\n"
        "  python manage.py count_instances --models business\n"
        "  python manage.py count_instances --apps backend reversion --models business version\n"
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--apps",
            dest="apps",
            nargs="+",
            default=[],
            help="Specify apps which should be listet. Empty means all apps.",
        )
        parser.add_argument(
            "--models",
            dest="models",
            nargs="+",
            default=[],
            help="Specify the models within the given apps which should be listed. Empty means all models within given apps.",  # noqa
        )

    def handle(self, *args: Any, **options: Any) -> None:
        self.options = options
        data = {}
        models = {f"{model._meta.app_label}.{model._meta.model_name}": model for model in self.get_models()}
        for identifier, model in sorted(models.items()):
            data[identifier] = model.objects.count()
        self.stdout.write(json.dumps(data, indent=2))

    def get_models(self) -> list[type[Model]]:
        if not self.options["apps"] and not self.options["models"]:
            return apps.get_models()

        invalid_apps = []
        app_configs = (
            [
                catch(
                    lambda: apps.get_app_config(app),
                    exception=LookupError,
                    handle=lambda e: invalid_apps.append(app),
                )
                for app in self.options["apps"]
            ]
            if self.options["apps"]
            else apps.app_configs.values()
        )

        if len(invalid_apps) == 1:
            raise CommandError(f"No installed app with label {invalid_apps[0]}.")
        elif len(invalid_apps) > 1:
            raise CommandError(f"No installed apps with labels {or_join(invalid_apps)}.")

        model_names = self.options["models"]
        if not model_names:
            return [model for app in app_configs for model in app.get_models()]

        models: list[type[Model]] = list(
            filter(
                None,
                [catch(lambda: app.get_model(model), exception=LookupError) for model in model_names for app in app_configs],
            )
        )

        self.validate_models(models)

        return models

    def validate_models(self, models: list[type[Model]]):
        invalid_model_names = [
            f"'{model_name}'"
            for model_name in set([model_name.lower() for model_name in self.options["models"]])
            - set([model.__name__.lower() for model in models])
        ]

        if len(invalid_model_names) == 1:
            raise CommandError(f"No model with name {invalid_model_names[0]}.")
        elif len(invalid_model_names) > 1:
            raise CommandError(f"No models with names {or_join(invalid_model_names)}.")


def or_join(value: list) -> str:
    return " or ".join(", ".join(value).rsplit(", ", 1))


def catch(
    func: Callable,
    *args: Any,
    handle: Callable = lambda e: None,
    exception: type[Exception] = Exception,
    **kwargs: Any,
):
    try:
        return func(*args, **kwargs)
    except exception as e:
        return handle(e)
