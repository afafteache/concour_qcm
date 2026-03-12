# C:\Users\HP ElieBook\Downloads\pfe\examens\admin.py

from django.contrib import admin
from .models import Examen

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('titre', 'session', 'date', 'actif', 'cree_par')
    list_filter  = ('actif',)