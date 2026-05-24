from django.db import models

from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)

from django.db.models import (
    Sum,
    F,
    DecimalField,
    ExpressionWrapper
)

from catalog.models import (
    CatalogueModule,
    CategorieEvaluation
)

from decimal import Decimal


# =====================================================
# INSCRIPTION
# =====================================================

class Inscription(models.Model):

    STATUS_CHOICES = (
        ('ouverte', 'Ouverte'),
        ('verrouillee', 'Verrouillée'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )

    annee_academique = models.CharField(
        max_length=20
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ouverte'
    )

    class Meta:

        unique_together = (
            'user',
            'annee_academique'
        )

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.annee_academique}"
        )

    # =========================
    # TOTAL COEFFICIENT
    # =========================

    def total_coefficient(self):

        total = self.modules.aggregate(

            total=Sum(
                'module__coefficient'
            )

        )['total']

        return total or 0

    # =========================
    # RESTE
    # =========================

    def reste(self):

        return 60 - self.total_coefficient()

    # =========================
    # CHECK AJOUT MODULE
    # =========================

    def can_add_module(self, module):

        if self.statut == 'verrouillee':

            return False

        nouveau_total = (
            self.total_coefficient()
            + module.coefficient
        )

        return nouveau_total <= 60

    # =========================
    # VERROUILLAGE
    # =========================

    def verifier_verrouillage(self):

        if self.total_coefficient() == 60:

            self.statut = "verrouillee"

        else:

            self.statut = "ouverte"

        self.save()

    # =========================
    # MOYENNE GENERALE
    # =========================

    def moyenne_generale(self):

        total_points = Decimal('0')

        total_coefficients = Decimal('0')

        modules = self.modules.select_related(
            'module'
        )

        for item in modules:

            moyenne_module = item.moyenne()

            if moyenne_module is None:
                continue

            coefficient = Decimal(
                str(item.module.coefficient)
            )

            total_points += (
                Decimal(str(moyenne_module))
                * coefficient
            )

            total_coefficients += coefficient

        if total_coefficients == 0:

            return Decimal('0')

        return round(

            total_points / total_coefficients,

            2
        )


# =====================================================
# MODULE CHOISI
# =====================================================

class ModuleChoisi(models.Model):

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.CASCADE,
        related_name='modules'
    )

    module = models.ForeignKey(
        CatalogueModule,
        on_delete=models.CASCADE
    )

    class Meta:

        unique_together = (
            'inscription',
            'module'
        )

    def __str__(self):

        return self.module.titre

    # =========================
    # VALIDATION
    # =========================

    def clean(self):

        if self.inscription.statut == 'verrouillee':

            raise ValidationError(
                "Votre inscription est verrouillée."
            )

        if not self.inscription.can_add_module(
            self.module
        ):

            total = (
                self.inscription
                .total_coefficient()
            )

            nouveau_total = (
                total
                + self.module.coefficient
            )

            raise ValidationError(

                f"Impossible d’ajouter "
                f"{self.module.titre} "
                f"(coefficient : "
                f"{self.module.coefficient}). "
                f"Total actuel : {total}. "
                f"Le total deviendrait "
                f"{nouveau_total}/60."
            )

    # =========================
    # SAVE
    # =========================

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

        self.inscription.verifier_verrouillage()

    # =========================
    # DELETE
    # =========================

    def delete(self, *args, **kwargs):

        inscription = self.inscription

        super().delete(*args, **kwargs)

        inscription.verifier_verrouillage()

    # =========================
    # MOYENNE MODULE
    # =========================

    def moyenne(self, type_note='officielle'):

        total_categories = (
            self.module.categories.count()
        )

        notes = self.notes.filter(
            type_note=type_note
        )

        if notes.count() < total_categories:

            return None

        result = notes.aggregate(

            moyenne=Sum(

                ExpressionWrapper(

                    F('valeur')
                    * F('categorie__poids'),

                    output_field=DecimalField(
                        max_digits=10,
                        decimal_places=2
                    )
                )
            )
        )

        total = result['moyenne']

        if total is None:

            return None

        return round(
            total / Decimal('100'),
            2
        )

    # =========================
    # MOYENNE ESTIMATION
    # =========================

    def moyenne_estimation(self):

        return self.moyenne(
            type_note='estimation'
        )


# =====================================================
# NOTE
# =====================================================

class Note(models.Model):

    TYPE_NOTE = (

        ('officielle', 'Officielle'),

        ('estimation', 'Estimation'),
    )

    module_choisi = models.ForeignKey(

        ModuleChoisi,

        on_delete=models.CASCADE,

        related_name='notes'
    )

    categorie = models.ForeignKey(

        CategorieEvaluation,

        on_delete=models.CASCADE
    )

    valeur = models.DecimalField(

        max_digits=4,

        decimal_places=2,

        validators=[

            MinValueValidator(0),

            MaxValueValidator(20)
        ]
    )

    type_note = models.CharField(

        max_length=20,

        choices=TYPE_NOTE,

        default='officielle'
    )

    date_saisie = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['date_saisie']

    def __str__(self):

        return (
            f"{self.module_choisi} - "
            f"{self.categorie} - "
            f"{self.type_note}"
        )

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)


# =====================================================
# NOTIFICATION
# =====================================================

class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.CharField(
        max_length=255
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.message


# =====================================================
# REMARQUE ENSEIGNANT
# =====================================================

class RemarqueEnseignant(models.Model):

    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='remarques_enseignants'
    )

    enseignant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='remarques_envoyees_enseignant'
    )

    module = models.ForeignKey(
        CatalogueModule,
        on_delete=models.CASCADE
    )

    contenu = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.etudiant.username} - "
            f"{self.module.titre}"
        )


# =====================================================
# SUIVI TUTEUR
# =====================================================

class SuiviTuteur(models.Model):

    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='suivis_tuteur'
    )

    tuteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='suivis_encadres'
    )

    remarque = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"Suivi - "
            f"{self.etudiant.username}"
        )