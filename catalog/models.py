from django.db import models

from django.contrib.auth.models import User

from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)

from django.core.exceptions import ValidationError


class CatalogueModule(models.Model):

    titre = models.CharField(
        max_length=200
    )

    coefficient = models.PositiveIntegerField(

        validators=[

            MinValueValidator(1),

            MaxValueValidator(60)
        ]
    )

    description = models.TextField(
        blank=True
    )

    est_actif = models.BooleanField(
        default=True
    )

    enseignant = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='modules_enseignes'
    )

    # =========================
    # VALIDATION
    # =========================

    def clean(self):

        if self.enseignant:

            if not hasattr(self.enseignant, 'profile'):

                raise ValidationError(
                    "Enseignant invalide."
                )

            if self.enseignant.profile.role != "enseignant":

                raise ValidationError(
                    "Utilisateur non enseignant."
                )

    def __str__(self):

        return self.titre


# =====================================================
# CATEGORIE EVALUATION
# =====================================================

class CategorieEvaluation(models.Model):
    
    module = models.ForeignKey(

        CatalogueModule,

        on_delete=models.CASCADE,

        related_name='categories'
    )

    nom = models.CharField(
        max_length=100
    )

    poids = models.DecimalField(

        max_digits=5,

        decimal_places=2
    )

    def __str__(self):

        return f"{self.nom} - {self.module.titre}"

    # =========================
    # VALIDATION POIDS
    # =========================

    def clean(self):

        total = sum(

            c.poids
            for c in self.module.categories.exclude(
                id=self.id
            )
        )

        total += self.poids

        if total > 100:

            raise ValidationError(
                "Le total des catégories dépasse 100%"
            )

    # =========================
    # SAVE
    # =========================

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)   
    
    
