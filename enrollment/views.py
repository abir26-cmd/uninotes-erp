from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import (
    Sum,
    F,
    DecimalField
)

from django.db.models.functions import Cast

from .models import (
    Inscription,
    ModuleChoisi,
    Note
)

from catalog.models import (
    CategorieEvaluation
)

import json


# =========================
# DASHBOARD ETUDIANT
# =========================

@login_required
def dashboard(request):

    inscription = get_object_or_404(
        Inscription,
        user=request.user
    )

    # optimisation ORM
    modules_qs = inscription.modules.select_related(
        'module'
    ).prefetch_related(
        'notes',
        'module__categories'
    )

    modules = []

    total_general = 0

    # -------------------------
    # MODULES + MOYENNES
    # -------------------------

    for mc in modules_qs:

        moyenne_module = mc.moyenne()

        if moyenne_module is not None:

            total_general += (
                moyenne_module
                * mc.module.coefficient
            )

        modules.append({

            "id": mc.id,

            "titre": mc.module.titre,

            "coefficient": mc.module.coefficient,

            "moyenne": moyenne_module,

            "categories": mc.module.categories.all(),

            "notes": mc.notes.all()

        })

    # -------------------------
    # MOYENNE GENERALE
    # -------------------------

    moyenne_generale = round(
        total_general / 60,
        2
    ) if total_general > 0 else 0

    # -------------------------
    # HISTORIQUE EVOLUTION
    # -------------------------

    notes = Note.objects.filter(
        module_choisi__inscription=inscription
    ).order_by("date_saisie")

    evolution = []

    running_total = 0

    count = 0

    for n in notes:

        running_total += n.valeur

        count += 1

        moyenne_temp = round(
            running_total / count,
            2
        )

        evolution.append({

            "date": n.date_saisie.strftime(
                "%Y-%m-%d %H:%M"
            ),

            "moyenne": moyenne_temp

        })

    # -------------------------
    # RENDER
    # -------------------------

    return render(
        request,
        "enrollment/dashboard.html",
        {

            "modules": modules,

            "moyenne_generale": moyenne_generale,

            "evolution": json.dumps(evolution)

        }
    )


# =========================
# AJOUT / MODIFICATION NOTES
# =========================

@login_required
def ajouter_note(request, module_id):

    profile = request.user.profile

    # enseignant uniquement
    if profile.role != "enseignant":

        messages.error(
            request,
            "Accès refusé"
        )

        return redirect("catalogue")

    module_choisi = get_object_or_404(

        ModuleChoisi,

        id=module_id
    )

    # sécurité :
    # enseignant responsable seulement

    if module_choisi.module.enseignant != request.user:

        messages.error(
            request,
            "Vous n'êtes pas responsable de ce module"
        )

        return redirect("enseignant_dashboard")

    # =====================================
    # SAVE NOTES
    # =====================================

    if request.method == "POST":

        for categorie in module_choisi.module.categories.all():

            valeur = request.POST.get(
                f"cat_{categorie.id}"
            )

            if valeur:

                valeur = float(valeur)

                # validation
                if valeur < 0 or valeur > 20:

                    messages.error(
                        request,
                        "La note doit être entre 0 et 20"
                    )

                    return redirect(
                        "enseignant_dashboard"
                    )

                # update or create

                Note.objects.update_or_create(

                    module_choisi=module_choisi,

                    categorie=categorie,

                    defaults={

                        "valeur": valeur
                    }
                )

        messages.success(
            request,
            "Notes enregistrées"
        )

        return redirect(
            "enseignant_dashboard"
        )

    return render(

        request,

        "enrollment/ajouter_note.html",

        {

            "module_choisi": module_choisi
        }
    )

