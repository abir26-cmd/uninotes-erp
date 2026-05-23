from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

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

    # enseignant responsable

    enseignant = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='modules_enseignes'
    )    
    def __str__(self):

        return self.titre


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