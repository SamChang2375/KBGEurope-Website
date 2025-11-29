# admin_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.dashboard_home, name='dashboard_home'),
    # Falls du Logout hast
    path('logout/', views.logout_view, name='logout'),
]
