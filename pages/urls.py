from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("menu/", views.menu_view, name="menu"),
    path("bestellen/", views.bestellen_view, name="bestellen"),
    path("catering/", views.catering_view, name="catering"),
    path("jobs/", views.jobs_view, name="jobs"),
    path("kontakt/", views.kontakt_view, name="kontakt"),
    path("impressum/", views.impressum, name="impressum"),
]
