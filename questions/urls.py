from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_liste, name='question_liste'),
    path('ajouter/', views.question_ajouter, name='question_ajouter'),
    path('<int:pk>/modifier/', views.question_modifier, name='question_modifier'),
    path('<int:pk>/confirmer-suppression/', views.question_confirmer_suppression, name='question_confirmer_suppression'),
    path('<int:pk>/supprimer/', views.question_supprimer, name='question_supprimer'),
    path('examen/creer/', views.examen_creer, name='examen_creer'),
    path('examen/mes-examens/', views.mes_examens, name='mes_examens'),
    path('questions/<int:pk>/confirmer/', views.question_confirmer_suppression, name='question_confirmer_suppression'),
]