from django.urls import path
from . import views

urlpatterns = [
    path('resultats/', views.resultat, name='resultats'),
]
