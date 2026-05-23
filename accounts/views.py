from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.models import User

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from .models import Profile

from enrollment.models import (
    Inscription,
    ModuleChoisi,
    Note
)

from catalog.models import (
    CatalogueModule,
    CategorieEvaluation
)

from catalog.forms import CatalogueModuleForm


# =========================================
# REGISTER
# =========================================

def register_view(request):

    tuteurs = Profile.objects.filter(
        role="tuteur"
    )

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        role = request.POST.get(
            "role"
        )

        tuteur_id = request.POST.get(
            "tuteur"
        )

        if not username or not password or not role:

            messages.error(
                request,
                "Tous les champs sont obligatoires"
            )

            return redirect("register")

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username déjà utilisé"
            )

            return redirect("register")

        user = User.objects.create_user(

            username=username,

            password=password
        )

        # =========================
        # ETUDIANT
        # =========================

        if role == "etudiant":

            tuteur = None

            if tuteur_id:

                try:

                    tuteur = User.objects.get(
                        id=tuteur_id
                    )

                except User.DoesNotExist:

                    tuteur = None

            Profile.objects.create(

                user=user,

                role=role,

                tuteur=tuteur
            )

        # =========================
        # ENSEIGNANT / TUTEUR
        # =========================

        else:

            Profile.objects.create(

                user=user,

                role=role
            )

        messages.success(
            request,
            "Compte créé avec succès"
        )

        return redirect("login")

    return render(

        request,

        "accounts/register.html",

        {

            "tuteurs": tuteurs
        }
    )


# =========================================
# LOGIN
# =========================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(

            request,

            username=username,

            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_superuser:

                return redirect("/admin/")

            profile = user.profile

            # =========================
            # ENSEIGNANT
            # =========================

            if profile.role == "enseignant":

                return redirect(
                    "enseignant_dashboard"
                )

            # =========================
            # TUTEUR
            # =========================

            if profile.role == "tuteur":

                return redirect(
                    "tutor_dashboard"
                )

            # =========================
            # ETUDIANT
            # =========================

            return redirect(
                "catalogue"
            )

        else:

            messages.error(

                request,

                "Identifiants invalides"
            )

    return render(

        request,

        "accounts/login.html"
    )


# =========================================
# LOGOUT
# =========================================

def logout_view(request):

    logout(request)

    return redirect("login")


# =========================================
# TUTOR DASHBOARD
# =========================================

@login_required
def tutor_dashboard(request):

    profile = request.user.profile

    if profile.role != "tuteur":

        return redirect("catalogue")

    etudiants = Profile.objects.filter(

        tuteur=request.user,

        role="etudiant"
    )

    data = []

    excellents = 0

    faibles = 0

    total_moyennes = 0

    total_etudiants = 0

    for e in etudiants:

        inscription = Inscription.objects.filter(
            user=e.user
        ).first()

        if not inscription:

            continue

        moyenne = inscription.moyenne_generale()

        if moyenne is None:

            moyenne = 0

        total_moyennes += moyenne

        total_etudiants += 1

        if moyenne >= 14:

            excellents += 1

        if moyenne < 10:

            faibles += 1

        data.append({

            "username": e.user.username,

            "moyenne": round(moyenne, 2),

            "modules": inscription.modules.all(),

            "statut": inscription.statut,

            "reste": inscription.reste()
        })

    moyenne_globale = 0

    if total_etudiants > 0:

        moyenne_globale = round(

            total_moyennes / total_etudiants,

            2
        )

    return render(

        request,

        "accounts/tutor_dashboard.html",

        {

            "etudiants": data,

            "moyenne_globale": moyenne_globale,

            "faibles": faibles,

            "excellents": excellents,

            "total_etudiants": total_etudiants
        }
    )


# =========================================
# AJOUTER MODULE
# =========================================

@login_required
def ajouter_module_enseignant(request):

    profile = request.user.profile

    if profile.role != "enseignant":

        return redirect("catalogue")

    if request.method == "POST":

        form = CatalogueModuleForm(
            request.POST
        )

        if form.is_valid():

            module = form.save(
                commit=False
            )

            module.enseignant = request.user

            module.save()

            messages.success(

                request,

                "Module ajouté avec succès"
            )

            return redirect(
                "enseignant_dashboard"
            )

    else:

        form = CatalogueModuleForm()

    return render(

        request,

        "accounts/ajouter_module.html",

        {

            "form": form
        }
    )


# =========================================
# DASHBOARD ENSEIGNANT
# =========================================

@login_required
def enseignant_dashboard(request):

    profile = request.user.profile

    if profile.role != "enseignant":

        return redirect("catalogue")

    modules = CatalogueModule.objects.filter(

        enseignant=request.user
    )

    data = []

    for module in modules:

        etudiants_data = []

        modules_choisis = ModuleChoisi.objects.filter(

            module=module
        )

        for mc in modules_choisis:

            notes = Note.objects.filter(

                module_choisi=mc
            )

            moyenne = mc.moyenne()

            etudiants_data.append({

                "username": mc.inscription.user.username,

                "notes": notes,

                "moyenne": moyenne,

                "module_choisi_id": mc.id

            })

        data.append({

            "module": module,

            "categories": module.categories.all(),

            "etudiants": etudiants_data

        })

    return render(

        request,

        "accounts/enseignant_dashboard.html",

        {

            "data": data
        }
    )


# =========================================
# MODIFIER MODULE
# =========================================

@login_required
def modifier_module_enseignant(request, module_id):

    module = get_object_or_404(

        CatalogueModule,

        id=module_id,

        enseignant=request.user
    )

    if request.method == "POST":

        form = CatalogueModuleForm(

            request.POST,

            instance=module
        )

        if form.is_valid():

            form.save()

            messages.success(

                request,

                "Module modifié avec succès"
            )

            return redirect(
                "enseignant_dashboard"
            )

    else:

        form = CatalogueModuleForm(
            instance=module
        )

    return render(

        request,

        "accounts/ajouter_module.html",

        {

            "form": form
        }
    )


# =========================================
# SUPPRIMER MODULE
# =========================================


@login_required
def supprimer_module_enseignant(request, module_id):

    module = get_object_or_404(

        CatalogueModule,

        id=module_id,

        enseignant=request.user
    )

    # =========================
    # CHECK ETUDIANTS INSCRITS
    # =========================

    existe = ModuleChoisi.objects.filter(
        module=module
    ).exists()

    if existe:

        messages.error(

            request,

            "Impossible de supprimer : des étudiants sont déjà inscrits dans ce module."
        )

        return redirect(
            "enseignant_dashboard"
        )

    # =========================
    # SUPPRESSION
    # =========================

    module.delete()

    messages.success(

        request,

        "Module supprimé avec succès."
    )

    return redirect(
        "enseignant_dashboard"
    )
    
    
# =========================================
# AJOUTER CATEGORIE
# =========================================

@login_required
def ajouter_categorie(request, module_id):

    profile = request.user.profile

    if profile.role != "enseignant":

        return redirect("catalogue")

    module = get_object_or_404(

        CatalogueModule,

        id=module_id,

        enseignant=request.user
    )

    if request.method == "POST":

        nom = request.POST.get("nom")

        poids = int(
            request.POST.get("poids")
        )

        total = sum(

            c.poids for c in module.categories.all()
        )

        nouveau_total = total + poids

        if nouveau_total > 100:

            messages.error(

                request,

                "Le total dépasse 100%"
            )

            return redirect(

                "ajouter_categorie",

                module_id=module.id
            )

        CategorieEvaluation.objects.create(

            module=module,

            nom=nom,

            poids=poids
        )

        messages.success(

            request,

            "Catégorie ajoutée avec succès"
        )

        return redirect(
            "enseignant_dashboard"
        )

    return render(

        request,

        "accounts/ajouter_categorie.html",

        {

            "module": module
        }
    )