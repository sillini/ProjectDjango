# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom d\'utilisateur'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Mot de passe'
    }))
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Mot de passe'})

from django import forms
from django.forms import inlineformset_factory
from .models import Cours, Section

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['titre', 'description', 'statut']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduction à la programmation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description détaillée du cours...'
            }),
            'statut': forms.Select(attrs={'class': 'form-select'})
        }

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['titre', 'contenu', 'fichier', 'cache']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la section'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Contenu de la section...'
            }),
           'fichier': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.ppt,.pptx,.txt,.zip'
            }),
            'cache': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

SectionFormSet = inlineformset_factory(
    Cours, Section,
    form=SectionForm,
    extra=1,
    can_delete=False
)
from django import forms
from .models import Travail

class TravailForm(forms.ModelForm):
    class Meta:
        model = Travail
        fields = ['titre', 'description', 'typeT', 'fichier', 'date_limite', 'statut']
        widgets = {
            'date_limite': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
from django import forms
from .models import Soumission

class SoumissionForm(forms.ModelForm):
    valider = forms.BooleanField(
        required=True,
        label="Je valide ma soumission",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Soumission
        fields = ['fichier']
        widgets = {
            'fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.zip,.rar'
            })
        }
    
    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            if fichier.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Le fichier ne doit pas dépasser 10MB")
            ext = fichier.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx', 'zip', 'rar']:
                raise forms.ValidationError("Format de fichier non supporté")
        return fichier