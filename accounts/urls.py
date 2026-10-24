from django.urls import path

from .views import (
    register,
    login,
    StoreProfileView,
    ChangePasswordView,
)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),

    path(
        "store-profile/",
        StoreProfileView.as_view(),
        name="store-profile",
    ),

    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
]
