from django.contrib import admin

# Register your models here.
from .models import CatalogueModule
from .models import CatalogueModule, CategorieEvaluation
admin.site.register(CatalogueModule)
admin.site.register(CategorieEvaluation)
