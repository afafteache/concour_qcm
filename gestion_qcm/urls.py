# C:\Users\HP ElieBook\Downloads\pfe\gestion_qcm\urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('examens.urls')),
    path('', include('concours.urls')),
    path('', include('resultats.urls')),
    # path('', include('questions.urls')),  # ← Afaf
]