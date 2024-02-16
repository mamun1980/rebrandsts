from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import login_view, register_user, STSLogoutView


urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", STSLogoutView.as_view(), name="logout")
]