from django.urls import path

from django_utils.webhooks.delete_user import views


urlpatterns = [
    path("api/auth/delete_user/inquire/", views.InquireDeleteView.as_view()),
    path("api/auth/delete_user/delete/", views.SubscribeDeleteView.as_view()),
]
