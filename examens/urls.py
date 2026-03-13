from django.urls import path
from . import views

urlpatterns = [
    # Dashboard admin
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),

    # Dashboard enseignant
    path('enseignant/dashboard/', views.dashboard_enseignant, name='dashboard_enseignant'),

    # Dashboard candidat
    path('dashboard/', views.dashboard_candidat, name='dashboard_candidat'),

    # Examen candidat
    path('examen/<int:examen_id>/', views.examen_view, name='examen'),

    # Résultat candidat
    path('resultat/<int:examen_id>/', views.resultat_view, name='resultat'),
]