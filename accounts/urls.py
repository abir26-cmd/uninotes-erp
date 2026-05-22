from django.urls import path

from .views import (

    register_view,

    login_view,

    logout_view,

    tutor_dashboard,

    enseignant_dashboard
)

urlpatterns = [

    path(
        "register/",
        register_view,
        name="register"
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),

    path(
        "tutor-dashboard/",
        tutor_dashboard,
        name="tutor_dashboard"
    ),

    path(
        "enseignant-dashboard/",
        enseignant_dashboard,
        name="enseignant_dashboard"
    ),
]