from django import forms

from .models import CatalogueModule


class CatalogueModuleForm(forms.ModelForm):

    class Meta:

        model = CatalogueModule

        fields = [

            'titre',

            'coefficient',

            'description',

            'est_actif'

        ]