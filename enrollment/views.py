from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from reportlab.pdfgen import canvas

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (
    HttpResponseForbidden,
    HttpResponse
)

from django.contrib.auth.models import User

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

    modules = []

    total_general = 0

    for mc in inscription.modules.all():

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

    moyenne_generale = round(
        total_general / 60,
        2
    ) if total_general > 0 else 0

    # =================================================
    # EVOLUTION NOTES
    # =================================================

    notes = Note.objects.filter(

        module_choisi__inscription=inscription

    ).order_by("date_saisie")

    evolution = []

    running_total = 0

    count = 0

    for note in notes:

        running_total += note.valeur

        count += 1

        evolution.append({

            "date": note.date_saisie.strftime(
                "%Y-%m-%d %H:%M"
            ),

            "moyenne": round(
                running_total / count,
                2
            )
        })

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


# =====================================================
# AJOUT / MODIFICATION NOTES
# =====================================================

@login_required
def ajouter_note(request, module_id):

    profile = request.user.profile

    # =================================================
    # ENSEIGNANT ONLY
    # =================================================

    if profile.role != "enseignant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    # =================================================
    # SECURITE
    # =================================================

    module_choisi = get_object_or_404(

        ModuleChoisi,

        id=module_id,

        module__enseignant=request.user
    )

    # =================================================
    # NOTES EXISTANTES
    # =================================================

    notes_existantes = {}

    notes_db = Note.objects.filter(
        module_choisi=module_choisi
    )

    for note in notes_db:

        notes_existantes[note.categorie.id] = note.valeur

    # =================================================
    # SAVE NOTES
    # =================================================

    if request.method == "POST":

        au_moins_une_note = False

        for categorie in module_choisi.module.categories.all():

            valeur = request.POST.get(
                f"cat_{categorie.id}"
            )

            # IGNORER CHAMPS VIDES

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

            # VALIDATION NOTE

            if valeur < 0 or valeur > 20:

                messages.error(

                    request,

                    "La note doit être entre 0 et 20."
                )

                return redirect(
                    "ajouter_note",
                    module_id=module_choisi.id
                )

            # AJOUT / MODIFICATION

            Note.objects.update_or_create(

                module_choisi=module_choisi,

                categorie=categorie,

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

        # =================================================
        # NOTIFICATION
        # =================================================

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

            "categories": module_choisi.module.categories.all(),

            "notes_existantes": notes_existantes
        }
    )


# =====================================================
# PROFILE
# =====================================================

@login_required
def profile(request):

    if request.method == "POST":

        user = request.user

        user.first_name = request.POST.get(
            'first_name'
        )

        user.last_name = request.POST.get(
            'last_name'
        )

        user.email = request.POST.get(
            'email'
        )

        user.profile.telephone = request.POST.get(
            'telephone'
        )

        password = request.POST.get(
            'password'
        )

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

    ).order_by('-created_at')

    suivis_tuteur = SuiviTuteur.objects.filter(

        etudiant=request.user

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
# EXPORT PDF
# =====================================================

@login_required
def export_pdf(request):

    if request.user.profile.role != "etudiant":

        return HttpResponseForbidden(
            "Accès refusé"
        )

    inscription = Inscription.objects.get(
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

        200,
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

        f"Email : {request.user.email}"
    )

    y = 690

    total = 0

    for mc in inscription.modules.all():

        moyenne = mc.moyenne()

        if moyenne is None:

            moyenne = 0

        total += (
            moyenne
            * mc.module.coefficient
        )

        p.drawString(

            50,
            y,

            f"{mc.module.titre} | Coef: {mc.module.coefficient} | Moyenne: {round(moyenne, 2)}"
        )

        y -= 25

    moyenne_generale = round(
        total / 60,
        2
    )

    p.setFont(
        "Helvetica-Bold",
        14
    )

    p.drawString(

        50,
        y - 20,

        f"Moyenne Générale : {moyenne_generale}"
    )

    p.save()

    return response