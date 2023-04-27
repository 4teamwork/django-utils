from django.urls import path

from django_utils.testing import views


urlpatterns = [
    path("setup", views.E2ETestSetupView.as_view()),
    path("teardown", views.E2ETestTearDownView.as_view()),
    path("login", views.TestingLoginView.as_view()),
    path("load_data", views.E2ETestLoadDataView.as_view()),
    path("ping", views.PingView.as_view()),
]
