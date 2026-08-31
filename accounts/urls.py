from django.urls import path

from .views import (
    login_view,
    logout_view,
    profile,
    register,
    edit_profile
)


urlpatterns = [
    path(
        "register/",
        register,
        name="register",
    ),

    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "logout/",
        logout_view,
        name="logout",
    ),

    path(
        "profile/",
        profile,
        name="profile",
    ),
    path(
    "profile/edit/",
    edit_profile,
    name="edit_profile",
),
]