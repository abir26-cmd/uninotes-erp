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

        widgets = {

            'titre': forms.TextInput(

                attrs={

                    'class': 'form-control'
                }
            ),

            'coefficient': forms.NumberInput(

                attrs={

                    'class': 'form-control'
                }
            ),

            'description': forms.Textarea(

                attrs={

                    'class': 'form-control',

                    'rows': 4
                }
            ),

            'est_actif': forms.CheckboxInput(

                attrs={

                    'class': 'form-check-input'
                }
            ),
        }

    # =========================
    # VALIDATION
    # =========================

    def clean_coefficient(self):

        coefficient = self.cleaned_data.get(
            'coefficient'
        )

        if coefficient <= 0:

            raise forms.ValidationError(
                "Coefficient invalide."
            )

        return coefficient