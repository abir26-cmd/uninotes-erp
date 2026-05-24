from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import (
    HttpResponseForbidden,
    HttpResponse
)

from reportlab.pdfgen import canvas

from .models import (
    Inscription,
    ModuleChoisi,
    Note,
    Notification,
    RemarqueEnseignant,
    SuiviTuteur
)

from .forms import (
    RemarqueEnseignantForm,
    SuiviTuteurForm
)

import json

from collections import defaultdict


# =====================================================
# DASHBOARD ETUDIANT
# =====================================================

@login_required
def dashboard(request):

    if request.user.profile.role != "etudiant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    inscription = get_object_or_404(

        Inscription,

        user=request.user
    )

    notifications = Notification.objects.filter(

        user=request.user

    ).order_by('-created_at')[:5]

    evolution_reelles = defaultdict(list)

    evolution_estimations = defaultdict(list)

    modules = []

    for mc in inscription.modules.select_related(
        "module"
    ).prefetch_related(
        "notes",
        "module__categories"
    ):

        # =========================================
        # COURBE EVOLUTION
        # =========================================

        notes_officielles = mc.notes.filter(
            type_note='officielle'
        ).order_by('date_saisie')

        notes_estimations = mc.notes.filter(
            type_note='estimation'
        ).order_by('date_saisie')

        for note in notes_officielles:

            evolution_reelles[
                mc.module.titre
            ].append(float(note.valeur))

        for note in notes_estimations:

            evolution_estimations[
                mc.module.titre
            ].append(float(note.valeur))

        # =========================================
        # RECOMMANDATION ENGINE
        # =========================================

        recommandation = None

        moyenne_module = mc.moyenne()

        moyenne_estimation = (
            mc.moyenne_estimation()
        )

        if moyenne_module is not None:

            if moyenne_module < 10:

                recommandation = (
                    "Module critique : "
                    "augmentation du temps de révision recommandée."
                )

            elif moyenne_module < 14:

                recommandation = (
                    "Résultat moyen : "
                    "continuez les exercices et les révisions."
                )

            else:

                recommandation = (
                    "Très bon niveau : "
                    "continuez sur cette progression."
                )

        elif moyenne_estimation is not None:

            if moyenne_estimation < 10:

                recommandation = (
                    "Estimation faible : "
                    "travail supplémentaire recommandé."
                )

            else:

                recommandation = (
                    "Bonne estimation : "
                    "continuez vos efforts."
                )

        modules.append({

            "id": mc.id,

            "titre": mc.module.titre,

            "coefficient": mc.module.coefficient,

            "moyenne": moyenne_module,

            "moyenne_estimation":
            moyenne_estimation,

            "recommendation":
            recommandation,

            "categories":
            mc.module.categories.all(),

            "notes":
            notes_officielles,

            "estimations":
            notes_estimations,
        })

    evolution = {

        "reelles": dict(
            evolution_reelles
        ),

        "estimations": dict(
            evolution_estimations
        )
    }

    return render(

        request,

        "enrollment/dashboard.html",

        {

            "inscription": inscription,

            "modules": modules,

            "moyenne_generale":
            inscription.moyenne_generale(),

            "evolution":
            json.dumps(evolution),

            "notifications":
            notifications,
        }
    )


# =====================================================
# AJOUT / MODIFICATION NOTES
# =====================================================

@login_required
def ajouter_note(request, module_id):

    profile = request.user.profile

    if profile.role != "enseignant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    module_choisi = get_object_or_404(

        ModuleChoisi,

        id=module_id,

        module__enseignant=request.user
    )

    categories = module_choisi.module.categories.all()

    # =================================================
    # NOTES EXISTANTES
    # =================================================

    notes_existantes = {}

    notes_db = Note.objects.filter(

        module_choisi=module_choisi,

        type_note='officielle'
    )

    for note in notes_db:

        notes_existantes[note.categorie.id] = note.valeur

    # =================================================
    # SAVE NOTES
    # =================================================

    if request.method == "POST":

        au_moins_une_note = False

        for categorie in categories:

            valeur = request.POST.get(
                f"cat_{categorie.id}"
            )

            if valeur == "" or valeur is None:

                continue

            au_moins_une_note = True

            try:

                valeur = float(valeur)

            except ValueError:

                messages.error(

                    request,

                    "Veuillez saisir un nombre valide."
                )

                return redirect(
                    "ajouter_note",
                    module_id=module_choisi.id
                )

            if valeur < 0 or valeur > 20:

                messages.error(

                    request,

                    "La note doit être entre 0 et 20."
                )

                return redirect(
                    "ajouter_note",
                    module_id=module_choisi.id
                )

            Note.objects.update_or_create(

                module_choisi=module_choisi,

                categorie=categorie,

                type_note='officielle',

                defaults={

                    "valeur": valeur
                }
            )

        if not au_moins_une_note:

            messages.error(

                request,

                "Veuillez saisir au moins une note."
            )

            return redirect(
                "ajouter_note",
                module_id=module_choisi.id
            )

        Notification.objects.create(

            user=module_choisi.inscription.user,

            message=f"Nouvelles notes ajoutées dans {module_choisi.module.titre}"
        )

        messages.success(

            request,

            "Notes enregistrées avec succès."
        )

        return redirect(
            "enseignant_dashboard"
        )

    return render(

        request,

        "enrollment/ajouter_note.html",

        {

            "module_choisi": module_choisi,

            "categories": categories,

            "notes_existantes": notes_existantes
        }
    )


# =====================================================
# PROFILE
# =====================================================

@login_required
def profile(request):

    user = request.user

    if request.method == "POST":

        user.first_name = request.POST.get(
            'first_name',
            ''
        )

        user.last_name = request.POST.get(
            'last_name',
            ''
        )

        user.email = request.POST.get(
            'email',
            ''
        )

        password = request.POST.get(
            'password'
        )

        if password:

            if len(password) < 6:

                messages.error(

                    request,

                    "Le mot de passe doit contenir au moins 6 caractères."
                )

                return redirect("profile")

            user.set_password(password)

        user.save()

        messages.success(

            request,

            "Profil mis à jour avec succès."
        )

        return redirect("profile")

    return render(

        request,

        'profile.html',

        {

            "user": user
        }
    )


# =====================================================
# NOTIFICATIONS
# =====================================================

@login_required
def notifications_page(request):

    notifications = Notification.objects.filter(

        user=request.user

    ).order_by('-created_at')

    notifications.update(
        is_read=True
    )

    return render(

        request,

        'notifications.html',

        {

            'notifications': notifications
        }
    )


# =====================================================
# REMARQUE ENSEIGNANT
# =====================================================

@login_required
def ajouter_remarque(request):

    if request.user.profile.role != "enseignant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

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
                'enseignant_dashboard'
            )

    else:

        form = RemarqueEnseignantForm()

    return render(

        request,

        'ajouter_remarque.html',

        {

            'form': form
        }
    )


# =====================================================
# SUIVI TUTEUR
# =====================================================

@login_required
def ajouter_suivi_tuteur(request):

    if request.user.profile.role != "tuteur":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    if request.method == "POST":

        form = SuiviTuteurForm(
            request.POST
        )

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


# =====================================================
# MES REMARQUES
# =====================================================

@login_required
def mes_remarques(request):

    if request.user.profile.role != "etudiant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    remarques_enseignants = RemarqueEnseignant.objects.filter(

        etudiant=request.user

    ).select_related(
        "enseignant",
        "module"
    ).order_by('-created_at')

    suivis_tuteur = SuiviTuteur.objects.filter(

        etudiant=request.user

    ).select_related(
        "tuteur"
    ).order_by('-created_at')

    return render(

        request,

        'mes_remarques.html',

        {

            'remarques_enseignants': remarques_enseignants,

            'suivis_tuteur': suivis_tuteur,
        }
    )


# =====================================================
# AJOUT ESTIMATION
# =====================================================

@login_required
def ajouter_estimation(request, module_id):

    if request.user.profile.role != "etudiant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    module_choisi = get_object_or_404(

        ModuleChoisi,

        id=module_id,

        inscription__user=request.user
    )

    categories = module_choisi.module.categories.all()

    if request.method == "POST":

        au_moins_une_note = False

        for categorie in categories:

            valeur = request.POST.get(
                f"cat_{categorie.id}"
            )

            if valeur == "" or valeur is None:

                continue

            au_moins_une_note = True

            try:

                valeur = float(valeur)

            except ValueError:

                messages.error(

                    request,

                    "Veuillez saisir un nombre valide."
                )

                return redirect(
                    "ajouter_estimation",
                    module_id=module_choisi.id
                )

            if valeur < 0 or valeur > 20:

                messages.error(

                    request,

                    "La note doit être entre 0 et 20."
                )

                return redirect(
                    "ajouter_estimation",
                    module_id=module_choisi.id
                )

            Note.objects.update_or_create(

                module_choisi=module_choisi,

                categorie=categorie,

                type_note='estimation',

                defaults={

                    "valeur": valeur
                }
            )

        if not au_moins_une_note:

            messages.error(

                request,

                "Veuillez saisir au moins une estimation."
            )

            return redirect(
                "ajouter_estimation",
                module_id=module_choisi.id
            )

        messages.success(

            request,

            "Estimations enregistrées."
        )

        return redirect("dashboard")

    notes_existantes = Note.objects.filter(

        module_choisi=module_choisi,

        type_note='estimation'
    )

    notes_dict = {}

    for note in notes_existantes:

        notes_dict[str(note.categorie.id)] = note.valeur

    return render(

        request,

        "enrollment/ajouter_estimation.html",

        {

            "module_choisi": module_choisi,

            "categories": categories,

            "notes_dict": notes_dict
        }
    )


# =====================================================
# EXPORT PDF
# =====================================================

@login_required
def export_pdf(request):

    if request.user.profile.role != "etudiant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    inscription = get_object_or_404(

        Inscription,

        user=request.user
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="releve_notes.pdf"'
    )

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 18)

    p.drawString(

        180,
        800,

        "Relevé de Notes"
    )

    p.setFont("Helvetica", 12)

    p.drawString(

        50,
        760,

        f"Nom : {request.user.get_full_name()}"
    )

    p.drawString(

        50,
        740,

        f"Username : {request.user.username}"
    )

    p.drawString(

        50,
        720,

        f"Email : {request.user.email}"
    )

    y = 670

    for mc in inscription.modules.select_related("module"):

        moyenne = mc.moyenne()

        if moyenne is None:

            moyenne = 0

        coefficient = mc.module.coefficient

        p.drawString(

            50,
            y,

            f"{mc.module.titre} | Coef: {coefficient} | Moyenne: {round(moyenne, 2)}"
        )

        y -= 25

        if y <= 80:

            p.showPage()

            y = 800

    p.setFont(
        "Helvetica-Bold",
        14
    )

    p.drawString(

        50,
        y - 20,

        f"Moyenne Générale : {inscription.moyenne_generale()}"
    )

    p.save()

    return response