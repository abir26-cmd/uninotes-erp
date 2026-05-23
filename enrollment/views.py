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
    Note,
    Notification
)

from catalog.models import (
    CategorieEvaluation
)

import json

from .forms import (
    RemarqueEnseignantForm,
    SuiviTuteurForm
)
from .models import Notification

# =========================
# DASHBOARD ETUDIANT
# =========================

@login_required
def dashboard(request):

    inscription = get_object_or_404(
        Inscription,
        user=request.user
    )
    
    notifications = Notification.objects.filter(
    user=request.user
    ).order_by('-created_at')[:5]
    
    
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

            "evolution": json.dumps(evolution),
            "notifications": notifications,

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





@login_required
def profile(request):

    if request.method == "POST":

        user = request.user

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        # TELEPHONE

        user.profile.telephone = request.POST.get('telephone')

        # PASSWORD

        password = request.POST.get('password')

        if password:
            user.set_password(password)

        user.save()
        user.profile.save()

        messages.success(
            request,
            "Profil mis à jour avec succès."
        )

    return render(
        request,
        'profile.html'
    )
    
# =========================    
# PAGE NOTIFICATIONS
# =========================
@login_required
def notifications_page(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # MARK AS READ

    notifications.update(is_read=True)

    return render(
        request,
        'notifications.html',
        {
            'notifications': notifications
        }
    )    
    

# =========================
# AJOUT REMARQUE (TUTEUR)
# ========================= 
@login_required
def ajouter_remarque(request):

    if request.user.profile.role != "enseignant":

        return redirect('dashboard')

    if request.method == "POST":

        form = RemarqueEnseignantForm(
            request.POST
        )

        if form.is_valid():

            remarque = form.save(
                commit=False
            )

            remarque.enseignant = request.user

            remarque.save()

            Notification.objects.create(

                user=remarque.etudiant,

                message=f"Nouvelle remarque dans le module {remarque.module.titre}"

            )

            messages.success(
                request,
                "Remarque envoyée avec succès."
            )

            return redirect(
                'dashboard'
            )

    else:

        form = RemarqueEnseignantForm()

    context = {

        'form': form

    }

    return render(

        request,

        'ajouter_remarque.html',

        context
    )
    
@login_required
def ajouter_suivi_tuteur(request):

    if request.user.profile.role != "tuteur":

        return redirect('dashboard')

    if request.method == "POST":

        form = SuiviTuteurForm(

            request.POST
        )

        # FILTRAGE ETUDIANTS
        form.fields['etudiant'].queryset = User.objects.filter(

            profile__tuteur=request.user,

            profile__role='etudiant'
        )

        if form.is_valid():

            suivi = form.save(

                commit=False
            )

            suivi.tuteur = request.user

            suivi.save()

            Notification.objects.create(

                user=suivi.etudiant,

                message="Nouvelle remarque de votre tuteur."
            )

            messages.success(

                request,

                "Remarque envoyée."
            )

            return redirect(

                'tutor_dashboard'
            )

    else:

        form = SuiviTuteurForm()

        form.fields['etudiant'].queryset = User.objects.filter(

            profile__tuteur=request.user,

            profile__role='etudiant'
        )

    return render(

        request,

        'ajouter_suivi_tuteur.html',

        {

            'form': form
        }
    )