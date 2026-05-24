from django.db import models

from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = (

        ('etudiant', 'Etudiant'),

        ('tuteur', 'Tuteur'),

        ('enseignant', 'Enseignant'),
    )

    user = models.OneToOneField(

        User,

        on_delete=models.CASCADE
    )

    role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES
    )

    # =========================
    # TELEPHONE
    # =========================

    telephone = models.CharField(

        max_length=20,

        blank=True,

        null=True
    )

    # =========================
    # TUTEUR
    # =========================

    tuteur = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="etudiants_suivis"
    )

    def __str__(self):

        return f"{self.user.username} ({self.role})"