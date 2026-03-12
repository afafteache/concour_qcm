# C:\Users\HP ElieBook\Downloads\pfe\examens\urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                         views.dashboard_admin,    name='dashboard_admin'),
    path('candidat/dashboard/',                views.dashboard_candidat, name='dashboard_candidat'),
    path('candidat/examen/<int:examen_id>/',   views.examen_view,        name='examen'),
    path('candidat/resultat/<int:examen_id>/', views.resultat_view,      name='resultat'),
]