from django import forms
from .models import SessionConcours, Concours


class SessionConcoursForm(forms.ModelForm):
    class Meta:
        model = SessionConcours
        fields = ['nom_session', 'concours', 'date_heure_debut', 'date_heure_fin', 'duree_minutes']
        widgets = {
            'date_heure_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_heure_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'