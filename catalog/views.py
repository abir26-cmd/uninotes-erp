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

# ====================================
# CATALOGUE + RECHERCHE
# ====================================
@login_required
def catalogue(request):

    profile = request.user.profile

    # étudiant seulement
    if profile.role != "etudiant":

        return redirect("dashboard")

    inscription = get_object_or_404(
        Inscription,
        user=request.user
    )
    # mise à jour automatique du statut
    inscription.verifier_verrouillage()
    modules = CatalogueModule.objects.filter(
        est_actif=True
    )

    modules_choisis = inscription.modules.values_list(
        "module_id",
        flat=True
    )

    total = inscription.total_coefficient()

    # ====================================
    # SUGGESTIONS INTELLIGENTES
    # ====================================

    moyenne = inscription.moyenne_generale()

    if moyenne is None or moyenne == 0:

        suggestions = modules.exclude(
            id__in=modules_choisis
        )[:3]

    elif moyenne < 10:

        suggestions = modules.filter(
            coefficient__lte=2
        ).exclude(
            id__in=modules_choisis
        )[:3]

    elif moyenne < 14:

        suggestions = modules.filter(
            coefficient__lte=4
        ).exclude(
            id__in=modules_choisis
        )[:3]

    else:

        suggestions = modules.filter(
            coefficient__gte=4
        ).exclude(
            id__in=modules_choisis
        )[:3]

    return render(

        request,

        "catalog/catalogue.html",

        {

            "modules": modules,

            "modules_choisis": modules_choisis,

            "total": total,

            "reste": inscription.reste(),

            "statut": inscription.statut,

            "suggestions": suggestions,

            

        }
    )

# ====================================
# AJOUT MODULE
# ====================================

@login_required
def ajouter_module(request, module_id):

    profile = request.user.profile

    if profile.role != "etudiant":

        return redirect("dashboard")

    inscription = get_object_or_404(
        Inscription,
        user=request.user
    )

    
    # INSCRIPTION VERROUILLEE
    if inscription.statut == "verrouillee":

        messages.error(
            request,
            "Inscription verrouillée"
        )

        return redirect("catalogue")

    module = get_object_or_404(
        CatalogueModule,
        id=module_id
    )

    # DEJA AJOUTE
    if ModuleChoisi.objects.filter(
        inscription=inscription,
        module=module
    ).exists():

        messages.warning(
            request,
            "Module déjà choisi"
        )

        return redirect("catalogue")

    # DEPASSEMENT 60
    if not inscription.can_add_module(module):

        messages.error(
            request,
            "Limite 60 points dépassée"
        )

        return redirect("catalogue")

    # AJOUT MODULE
    ModuleChoisi.objects.create(

        inscription=inscription,

        module=module
    )

    inscription.verifier_verrouillage()

    messages.success(
        request,
        "Module ajouté avec succès"
    )

    return redirect("catalogue")


# ====================================
# SUPPRIMER MODULE
# ====================================

@login_required
def supprimer_module(request, module_id):

    profile = request.user.profile

    if profile.role != "etudiant":

        return redirect("dashboard")

    inscription = get_object_or_404(
        Inscription,
        user=request.user
    )

    # INSCRIPTION VERROUILLEE
    if inscription.statut == "verrouillee":

        messages.error(
            request,
            "Inscription verrouillée"
        )

        return redirect("catalogue")

    module_choisi = get_object_or_404(

        ModuleChoisi,

        inscription=inscription,

        module_id=module_id
    )

    module_choisi.delete()
    inscription.verifier_verrouillage()


    messages.success(
        request,
        "Module supprimé"
    )

    return redirect("catalogue")


@login_required
def ajouter_module_enseignant(request):

    if request.user.profile.role != "enseignant":

        return redirect("dashboard")

    if request.method == "POST":

        form = CatalogueModuleForm(request.POST)

        if form.is_valid():

            module = form.save(commit=False)

            module.enseignant = request.user

            module.save()

            module = form.save(commit=False)
            module.enseignant = request.user
            module.save()

            messages.success(
                request,
                "Module ajouté avec succès."
            )

            return redirect("enseignant_dashboard")

    else:

        form = CatalogueModuleForm()

    return render(

        request,

        "catalog/ajouter_module_enseignant.html",

        {
            "form": form
        }
    )