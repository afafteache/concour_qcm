# C:\Users\HP ElieBook\Downloads\pfe\accounts\admin.py

from django.contrib import admin
from .models import Profil

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display  = ('user', 'cin', 'role')
    list_filter   = ('role',)
    search_fields = ('cin', 'user__first_name', 'user__last_name')