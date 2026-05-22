from django.contrib import admin

# Register your models here.

from .models import Inscription, ModuleChoisi, Note

admin.site.register(Inscription)
admin.site.register(ModuleChoisi)
admin.site.register(Note)