from django.contrib import admin
from django.contrib import messages

from .models import (
    CatalogueModule,
    CategorieEvaluation
)

from enrollment.models import ModuleChoisi


@admin.register(CatalogueModule)
class CatalogueModuleAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "coefficient",
        "enseignant",
        "est_actif"
    )

    # =========================
    # SUPPRESSION SIMPLE
    # =========================

    def delete_model(self, request, obj):

        if ModuleChoisi.objects.filter(
            module=obj
        ).exists():

            self.message_user(

                request,

                "Impossible de supprimer : module déjà choisi par des étudiants.",

                level=messages.ERROR
            )

            return

        super().delete_model(
            request,
            obj
        )

    # =========================
    # SUPPRESSION MULTIPLE
    # =========================

    def delete_queryset(self, request, queryset):

        modules_bloques = []

        for module in queryset:

            if ModuleChoisi.objects.filter(
                module=module
            ).exists():

                modules_bloques.append(
                    module.titre
                )

            else:

                module.delete()

        if modules_bloques:

            self.message_user(

                request,

                "Suppression refusée pour : "
                + ", ".join(modules_bloques),

                level=messages.ERROR
            )


admin.site.register(CategorieEvaluation)