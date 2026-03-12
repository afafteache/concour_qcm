# C:\Users\HP ElieBook\Downloads\pfe\resultats\admin.py

from django.contrib import admin
from .models import Resultat

@admin.register(Resultat)
class ResultatAdmin(admin.ModelAdmin):
    list_display  = ('candidat', 'examen', 'score', 'date_passage')
    list_filter   = ('examen',)
    search_fields = ('candidat__first_name', 'candidat__last_name')