from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from catalog.models import CatalogueModule, CategorieEvaluation
from django.shortcuts import (
    render,
    
)
from decimal import Decimal
from django.db.models import Sum
from decimal import Decimal


from django.db.models import F, Sum, DecimalField
from django.db.models.functions import Cast

class Inscription(models.Model):

    STATUS_CHOICES = (
        ('ouverte', 'Ouverte'),
        ('verrouillee', 'Verrouillée'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ouverte'
    )

    def __str__(self):
        return self.user.username

    def total_coefficient(self):
        return sum(item.module.coefficient for item in self.modules.all())

    def reste(self):
        return 60 - self.total_coefficient()

    def can_add_module(self, module):
        nouveau_total = self.total_coefficient() + module.coefficient
        return nouveau_total <= 60

    
    def verifier_verrouillage(self):
        if self.total_coefficient() == 60:
            self.statut = 'verrouillee'
            self.save()
    
    
    def moyenne_generale(self):
    
      modules = self.modules.all()

      total = Decimal('0')

      for item in modules:
          moyenne_module = item.moyenne()

          if moyenne_module is None:
              continue

          total += Decimal(str(moyenne_module)) * Decimal(str(item.module.coefficient))

      return total / Decimal('60')
    
    
    def has_notes(self):
    
        return Note.objects.filter(

            module_choisi__inscription=self

        ).exists()
    
    
    def has_notes(self):
    
        return Note.objects.filter(

            module_choisi__inscription=self

        ).exists()
    
    
    def dashboard(request):
    
       inscription = Inscription.objects.get(user=request.user)

       modules = inscription.modules.all()

       context = {
           "inscription": inscription,
           "modules": modules,
           "moyenne_generale": inscription.moyenne_generale()
       }

       return render(request, "dashboard.html", context)

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
        unique_together = ('inscription', 'module')

    def __str__(self):
        return self.module.titre

    # -------------------
    # VALIDATION
    # -------------------

    def clean(self):
        if not self.inscription.can_add_module(self.module):
            raise ValidationError(
                "Impossible: dépassement de 60 points (limite 60)"
            )

    def save(self, *args, **kwargs):

        if not self.inscription.can_add_module(self.module):
            raise ValidationError(
                "Impossible: dépassement de 60 points (limite 60)"
            )

        super().save(*args, **kwargs)

        self.inscription.verifier_verrouillage()

    # -------------------
    # MOYENNE MODULE
    # -------------------

    def moyenne(self):
    
        notes = self.notes.annotate(

            weighted=Cast(
                F('valeur'),
                DecimalField()
            ) * F('categorie__poids')

        ).aggregate(

            total=Sum('weighted')

        )['total']

        if not notes:
            return None

        return notes / Decimal('100')
    
    
    


class Note(models.Model):

    module_choisi = models.ForeignKey(
        ModuleChoisi,
        on_delete=models.CASCADE,
        related_name='notes'
    )

    categorie = models.ForeignKey(
        CategorieEvaluation,
        on_delete=models.CASCADE
    )

    valeur = models.FloatField()

    date_saisie = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('module_choisi', 'categorie')

    def clean(self):

        if self.valeur < 0 or self.valeur > 20:
            raise ValidationError(
                "Note doit être entre 0 et 20"
            )

    def __str__(self):
        return f"{self.module_choisi} - {self.categorie}"
    
    


# -------------------
# NOTIFICATIONS
# -------------------

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


# -------------------
# REMARQUE ENSEIGNANT
# -------------------

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

        return f"{self.etudiant.username} - {self.module.titre}"


# -------------------
# SUIVI TUTEUR
# -------------------
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

        return f"Suivi - {self.etudiant.username}"