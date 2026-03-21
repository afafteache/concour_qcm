from django.urls import path
from . import views

urlpatterns = [
    path('resultats/', views.resultats_liste, name='resultats_liste'),
    path('candidats/import/', views.import_candidats_excel, name='import_candidats'),
    path('candidats/modele/', views.telecharger_modele_excel, name='modele_excel'),
    path('candidats/<int:profil_id>/supprimer/', views.supprimer_candidat, name='supprimer_candidat'),
]