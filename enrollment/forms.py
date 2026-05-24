from django import forms

from django.contrib.auth.models import User

from .models import (
    RemarqueEnseignant,
    SuiviTuteur
)

from enrollment.models import ModuleChoisi


# =====================================================
# REMARQUE ENSEIGNANT FORM
# =====================================================

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

    # =========================
    # VALIDATION CONTENU
    # =========================

    def clean_contenu(self):

        contenu = self.cleaned_data.get(
            'contenu'
        )

        if len(contenu.strip()) < 5:

            raise forms.ValidationError(
                "La remarque est trop courte."
            )

        return contenu


# =====================================================
# SUIVI TUTEUR FORM
# =====================================================

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

    # =========================
    # VALIDATION REMARQUE
    # =========================

    def clean_remarque(self):

        remarque = self.cleaned_data.get(
            'remarque'
        )

        if len(remarque.strip()) < 5:

            raise forms.ValidationError(
                "La remarque est trop courte."
            )

        return remarque