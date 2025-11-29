# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("menu/", views.menu_view, name="menu"),
    path("bestellen/", views.bestellen_view, name="bestellen"),
]
