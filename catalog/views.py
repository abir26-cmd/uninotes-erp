from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CatalogueModuleForm
from .models import CatalogueModule

from enrollment.models import (
    Inscription,
    ModuleChoisi,
)


# =====================================================
# CATALOGUE ETUDIANT
# =====================================================

@login_required
def catalogue(request):

    profile = request.user.profile

    # =========================================
    # ACCES ETUDIANT SEULEMENT
    # =========================================

    if profile.role != "etudiant":

        return redirect("dashboard")

    # =========================================
    # INSCRIPTION
    # =========================================

    inscription = get_object_or_404(

        Inscription,

        user=request.user
    )

    # mise à jour automatique statut
    inscription.verifier_verrouillage()

    # =========================================
    # MODULES ACTIFS
    # =========================================

    modules = CatalogueModule.objects.filter(

        est_actif=True

    ).select_related('enseignant')

    # =========================================
    # MODULES DEJA CHOISIS
    # =========================================

    modules_choisis = inscription.modules.values_list(

        "module_id",

        flat=True
    )

    # =========================================
    # STATISTIQUES
    # =========================================

    total = inscription.total_coefficient()

    reste = inscription.reste()

    moyenne = inscription.moyenne_generale()

    # =========================================
    # MODULES DISPONIBLES
    # =========================================

    modules_disponibles = modules.exclude(

        id__in=modules_choisis
    )

    # =========================================
    # SUGGESTIONS INTELLIGENTES
    # =========================================

    # Etudiant sans notes
    if moyenne is None or moyenne == 0:

        suggestions = modules_disponibles.filter(

            coefficient__lte=reste

        ).order_by('coefficient')[:3]

    # Etudiant faible
    elif moyenne < 10:

        suggestions = modules_disponibles.filter(

            coefficient__lte=min(reste, 20)

        ).order_by('coefficient')[:3]

    # Etudiant moyen
    elif moyenne < 14:

        suggestions = modules_disponibles.filter(

            coefficient__lte=min(reste, 30)

        ).order_by('coefficient')[:3]

    # Bon étudiant
    else:

        suggestions = modules_disponibles.filter(

            coefficient__lte=reste

        ).order_by('-coefficient')[:3]

    # =========================================
    # RENDER
    # =========================================

    context = {

        "modules": modules,

        "modules_choisis": modules_choisis,

        "total": total,

        "reste": reste,

        "statut": inscription.statut,

        "suggestions": suggestions,

        "moyenne_generale": moyenne,
    }

    return render(

        request,

        "catalog/catalogue.html",

        context
    )


# =====================================================
# AJOUT MODULE
# =====================================================

@login_required
def ajouter_module(request, module_id):

    profile = request.user.profile

    # =========================================
    # ACCES ETUDIANT
    # =========================================

    if profile.role != "etudiant":

        return redirect("dashboard")

    inscription = get_object_or_404(

        Inscription,

        user=request.user
    )

    # =========================================
    # INSCRIPTION VERROUILLEE
    # =========================================

    if inscription.statut == "verrouillee":

        messages.error(

            request,

            "Votre inscription est verrouillée."
        )

        return redirect("catalogue")

    # =========================================
    # MODULE
    # =========================================

    module = get_object_or_404(

        CatalogueModule,

        id=module_id,

        est_actif=True
    )

    # =========================================
    # MODULE DEJA CHOISI
    # =========================================

    if ModuleChoisi.objects.filter(

        inscription=inscription,

        module=module

    ).exists():

        messages.warning(

            request,

            "Ce module est déjà sélectionné."
        )

        return redirect("catalogue")

    # =========================================
    # DEPASSEMENT 60 POINTS
    # =========================================

    if not inscription.can_add_module(module):

        messages.error(

            request,

            f"Impossible d’ajouter "
            f"{module.titre}. "
            f"Limite des 60 points dépassée."
        )

        return redirect("catalogue")

    # =========================================
    # AJOUT MODULE
    # =========================================

    ModuleChoisi.objects.create(

        inscription=inscription,

        module=module
    )

    # mise à jour statut
    inscription.verifier_verrouillage()

    messages.success(

        request,

        "Module ajouté avec succès."
    )

    return redirect("catalogue")


# =====================================================
# SUPPRESSION MODULE
# =====================================================

@login_required
def supprimer_module(request, module_id):

    profile = request.user.profile

    # =========================================
    # ACCES ETUDIANT
    # =========================================

    if profile.role != "etudiant":

        return redirect("dashboard")

    inscription = get_object_or_404(

        Inscription,

        user=request.user
    )

    # =========================================
    # INSCRIPTION VERROUILLEE
    # =========================================

    if inscription.statut == "verrouillee":

        messages.error(

            request,

            "Votre inscription est verrouillée."
        )

        return redirect("catalogue")

    # =========================================
    # MODULE CHOISI
    # =========================================

    module_choisi = get_object_or_404(

        ModuleChoisi,

        inscription=inscription,

        module_id=module_id
    )

    module_choisi.delete()

    # mise à jour statut
    inscription.verifier_verrouillage()

    messages.success(

        request,

        "Module supprimé avec succès."
    )

    return redirect("catalogue")


# =====================================================
# AJOUT MODULE ENSEIGNANT
# =====================================================

@login_required
def ajouter_module_enseignant(request):

    # =========================================
    # ACCES ENSEIGNANT
    # =========================================

    if request.user.profile.role != "enseignant":

        return redirect("dashboard")

    # =========================================
    # FORMULAIRE
    # =========================================

    if request.method == "POST":

        form = CatalogueModuleForm(request.POST)

        if form.is_valid():

            module = form.save(commit=False)

            module.enseignant = request.user

            module.save()

            messages.success(

                request,

                "Module ajouté avec succès."
            )

            return redirect(
                "enseignant_dashboard"
            )

    else:

        form = CatalogueModuleForm()

    # =========================================
    # RENDER
    # =========================================

    return render(

        request,

        "catalog/ajouter_module_enseignant.html",

        {
            "form": form
        }
    )