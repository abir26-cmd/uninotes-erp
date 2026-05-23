from django.urls import path

from .views import (

    register_view,

    login_view,

    logout_view,

    tutor_dashboard,

    enseignant_dashboard,

    ajouter_module_enseignant,

    modifier_module_enseignant,

    supprimer_module_enseignant,
    
    ajouter_categorie,
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

    path(
        "ajouter-module-enseignant/",
        ajouter_module_enseignant,
        name="ajouter_module_enseignant"
    ),

    path(
        "modifier-module/<int:module_id>/",
        modifier_module_enseignant,
        name="modifier_module_enseignant"
    ),

    path(
        "supprimer-module/<int:module_id>/",
        supprimer_module_enseignant,
        name="supprimer_module_enseignant"
    ),
    path(
    "ajouter-categorie/<int:module_id>/",
    ajouter_categorie,
    name="ajouter_categorie"
    ),

]