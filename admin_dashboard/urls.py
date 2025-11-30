from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    path(
        "requests/catering/<int:pk>/answer/",
        views.answer_catering_request,
        name="answer_catering_request",
    ),
    path(
        "requests/contact/<int:pk>/answer/",
        views.answer_contact_request,
        name="answer_contact_request",
    ),
    path(
        "logout/",
        LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    # NEU:
    path(
        "media/update/",
        views.update_site_image,
        name="dashboard_media_update",
    ),
]
