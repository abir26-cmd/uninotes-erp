from django.shortcuts import (
    #send template to browser
    render,
    #display the html page of the url
    redirect
)
# user predefined model in django 
from django.contrib.auth.models import User

from django.contrib.auth import (
    # authenticate user
    authenticate,
    #stay connected
    login,
    #close session
    logout
)
#empêcher l'accès à une page sans être connecté
from django.contrib.auth.decorators import login_required
#messages d'erreur ou de succès
from django.contrib import messages

from .models import Profile

from enrollment.models import (
    Inscription,
    ModuleChoisi
)


# =========================================
# REGISTER /signup
# =========================================

def register_view(request):

    # récupérer tuteurs pour le dropdown
    tuteurs = Profile.objects.filter(
        role="tuteur"
    )
    # if user submit the form
    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        role = request.POST.get("role")

        tuteur_id = request.POST.get("tuteur")

        # validation
        if not username or not password or not role:

            messages.error(
                request,
                "Tous les champs sont obligatoires"
            )
            #reload the page
            return redirect("register")

        # username déjà utilisé
        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username déjà utilisé"
            )

            return redirect("register")

        # create user
        user = User.objects.create_user(

            username=username,

            password=password
        )

        # ====================================
        # ETUDIANT
        # ====================================

        if role == "etudiant":

            tuteur = None

            # récupérer tuteur
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

        # ====================================
        # TUTEUR / ENSEIGNANT
        # ====================================

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

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(

            request,

            username=username,

            password=password
        )

        if user is not None:

            login(request, user)

            # ====================================
            # ADMIN
            # ====================================

            if user.is_superuser:

                return redirect("/admin/")

            profile = user.profile

            # ====================================
            # ENSEIGNANT
            # ====================================

            if profile.role == "enseignant":

                return redirect(
                    "enseignant_dashboard"
                )

            # ====================================
            # TUTEUR
            # ====================================

            if profile.role == "tuteur":

                return redirect(
                    "tutor_dashboard"
                )

            # ====================================
            # ETUDIANT
            # ====================================

            return redirect("catalogue")

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

    # sécurité
    if profile.role != "tuteur":

        return redirect("catalogue")

    # étudiants suivis
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

        # sécurité None
        if moyenne is None:

            moyenne = 0

        # stats
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

    # moyenne globale
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
# ENSEIGNANT DASHBOARD
# =========================================

@login_required
def enseignant_dashboard(request):

    profile = request.user.profile

    # sécurité
    if profile.role != "enseignant":

        return redirect("catalogue")

    # modules de l'enseignant
    modules = request.user.modules_enseignes.all()

    data = []

    for module in modules:

        inscriptions = ModuleChoisi.objects.filter(
            module=module
        )

        etudiants = []

        for mc in inscriptions:

            etudiants.append({

                "module_choisi_id": mc.id,

                "username": mc.inscription.user.username,

                "moyenne": mc.moyenne(),

                "notes": mc.notes.all()
            })

        data.append({

            "module": module,

            "etudiants": etudiants
        })

    return render(

        request,

        "accounts/enseignant_dashboard.html",

        {

            "data": data
        }
    )