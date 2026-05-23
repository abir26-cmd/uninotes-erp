from django.urls import path

from .views import (
    dashboard,
    ajouter_note
)
from enrollment import views

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
    path(
    'profile/',
    views.profile,
    name='profile'
),
    path(
    'notifications/',
    views.notifications_page,
    name='notifications'
),
    path(
    'ajouter-remarque/',
    views.ajouter_remarque,
    name='ajouter_remarque'
),
    
    path(
    'ajouter-suivi-tuteur/',
    views.ajouter_suivi_tuteur,
    name='ajouter_suivi_tuteur'
),
    path(
    'mes-remarques/',
    views.mes_remarques,
    name='mes_remarques'
),
    path(
    'export-pdf/',
    views.export_pdf,
    name='export_pdf'
),
]