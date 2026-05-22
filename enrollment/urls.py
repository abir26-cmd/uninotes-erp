from django.urls import path

from .views import (
    dashboard,
    ajouter_note
)

urlpatterns = [

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    path(
        "note/<int:module_id>/",
        ajouter_note,
        name="ajouter_note"
    ),
]