from rest_framework.routers import DefaultRouter
from django.urls import path

from accounts.views import (
    LoginViewSet,
    RegistrationViewSet,
    RefreshViewSet,
    VerifyAccountView,
    DeactivateAccountView,
    LogoutView,
)


routes = DefaultRouter()

# AUTHENTICATION
routes.register(r"login", LoginViewSet, basename="auth-login")
routes.register(r"register", RegistrationViewSet, basename="auth-register")
routes.register(r"refresh", RefreshViewSet, basename="auth-refresh")

urlpatterns = [
    *routes.urls,
    path(
        "activate/<slug:uidb64>/<slug:token>/",
        VerifyAccountView.as_view({"get": "retrieve"}),
        name="activate",
    ),
    path(
        "deactivate-account/",
        DeactivateAccountView.as_view(),
        name="deactivate-account",
    ),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
]
