from django.contrib import admin

# Register your models here.

from .models import (
    Inscription,
    ModuleChoisi,
    Note,
    Notification,
    RemarqueEnseignant,
    SuiviTuteur
)
admin.site.register(Inscription)
admin.site.register(ModuleChoisi)
admin.site.register(Note)
admin.site.register(Notification)

admin.site.register(RemarqueEnseignant)

admin.site.register(SuiviTuteur)