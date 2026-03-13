from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_enseignant, name='dashboard_enseignant'),

    path('', views.question_liste, name='question_liste'),
    path('ajouter/', views.question_ajouter, name='question_ajouter'),
    path('<int:pk>/modifier/', views.question_modifier, name='question_modifier'),
    path('<int:pk>/supprimer/', views.question_supprimer, name='question_supprimer'),
]