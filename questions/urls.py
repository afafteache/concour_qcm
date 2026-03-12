from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_liste, name='question_liste'),
]