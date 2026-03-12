# C:\Users\HP ElieBook\Downloads\pfe\resultats\urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('resultats/', views.resultats_liste, name='resultats_liste'),
]