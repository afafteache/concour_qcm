from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_candidat, name='dashboard_candidat'),
    path('examen/<int:examen_id>/', views.passer_examen, name='passer_examen'),
]
