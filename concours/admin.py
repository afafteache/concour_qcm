# C:\Users\HP ElieBook\Downloads\pfe\concours\admin.py

from django.contrib import admin
from .models import Module, Concours, SessionConcours

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('nom',)

@admin.register(Concours)
class ConcoursAdmin(admin.ModelAdmin):
    list_display = ('titre', 'module', 'date', 'duree_minutes')

@admin.register(SessionConcours)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('nom_session', 'concours', 'date_heure_debut', 'etat', 'examen_lance')
    list_filter  = ('etat', 'examen_lance')