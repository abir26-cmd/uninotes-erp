from django.db import models

from django.contrib.auth.models import User


class Profile(models.Model):
    # tuple of choices for the role field
    ROLE_CHOICES = (
        #('value_in_database', 'text_displayed')
        ('etudiant', 'Etudiant'),

        ('tuteur', 'Tuteur'),

        ('enseignant', 'Enseignant'),
    )
    # one-to-one relationship with user_and_profile 
    # each user has one profile 
    # and each profile is linked to one user
    #relation 1 ↔ 1
    user = models.OneToOneField(

        User,
        # when a user is deleted, the profile is also deleted

        on_delete=models.CASCADE
    )

    role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES
    )

    # suivi pédagogique
    #1 tuteur → plusieurs étudiants
    
    tuteur = models.ForeignKey(

        User,
        # when a tuteur is deleted, 
        # the field is set to null
        on_delete=models.SET_NULL,

        null=True,

        blank=True,
        #related stdents followed by the tutor
        related_name="etudiants_suivis"
    )

    def __str__(self):

        return f"{self.user.username} ({self.role})"