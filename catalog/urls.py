from django.urls import path

from accounts import views

from .views import (
    catalogue,
    ajouter_module,
    supprimer_module
)

urlpatterns = [

    path(
        "",
        catalogue,
        name="catalogue"
    ),

    path(
        "ajouter/<int:module_id>/",
        ajouter_module,
        name="ajouter_module"
    ),

    path(
        "supprimer/<int:module_id>/",
        supprimer_module,
        name="supprimer_module"
    ),
path(
    "ajouter-module-enseignant/",
    views.ajouter_module_enseignant,
    name="ajouter_module_enseignant"
),
]