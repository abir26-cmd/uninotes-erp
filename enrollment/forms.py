from django import forms

from .models import (
    RemarqueEnseignant,
    SuiviTuteur
)


class RemarqueEnseignantForm(forms.ModelForm):

    class Meta:

        model = RemarqueEnseignant

        fields = [
            'etudiant',
            'module',
            'contenu'
        ]

        widgets = {

            'contenu': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),

            'etudiant': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'module': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
        }


class SuiviTuteurForm(forms.ModelForm):

    class Meta:

        model = SuiviTuteur

        fields = [
            'etudiant',
            'remarque'
        ]

        widgets = {

            'remarque': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),

            'etudiant': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
        }