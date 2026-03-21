from django.urls import path
from . import views

urlpatterns = [
    # Candidat
    path('passer/<int:examen_id>/', views.examen_view, name='examen'),
    path('resultat/<int:examen_id>/', views.resultat_view, name='resultat'),
    path('dashboard/', views.dashboard_candidat, name='dashboard_candidat'),

    # Admin
    path('admin/examens/', views.admin_examens, name='admin_examens'),
    path('admin/examens/<int:examen_id>/valider/', views.admin_valider_examen, name='admin_valider_examen'),
    path('admin/examens/<int:examen_id>/session/', views.creer_session_pour_examen, name='creer_session_pour_examen'),
    path('admin/examens/<int:examen_id>/supprimer/', views.admin_supprimer_examen, name='admin_supprimer_examen'),

    # Enseignant
    path('enseignant/examens/<int:examen_id>/supprimer/', views.enseignant_supprimer_examen, name='enseignant_supprimer_examen'),
]