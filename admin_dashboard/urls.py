from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    # Login / Logout
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),

    # Dashboard
    path("dashboard/", views.dashboard_home, name="dashboard_home"),

    # Anfragen beantworten
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

    # ⭐ Benutzer-Management
    path(
        "users/create/",
        views.dashboard_create_user,
        name="dashboard_create_user",       # <— URL-Name
    ),
    path(
        "users/<int:pk>/delete/",
        views.dashboard_delete_user,
        name="dashboard_delete_user",       # <— passt jetzt zum Template
    ),

    # ⭐ Passwort-Zwangsänderung beim ersten Login
    path(
        "password/force-change/",
        views.force_password_change,
        name="force_password_change",       # <— passt zu redirect("force_password_change")
    ),

    # ⭐ Medien-Update (Medien-Tab)
    path(
        "media/update/",
        views.dashboard_media_update,
        name="dashboard_media_update",
    ),
]
