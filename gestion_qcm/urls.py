from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Pages principales et authentification
    path('', include('accounts.urls')),

    # Partie candidat
    path('candidat/', include('examens.urls')),

    # Partie admin
    path('gestion/', include('concours.urls')),
    path('resultats/', include('resultats.urls')),

    # Partie enseignant
    path('questions/', include('questions.urls')),
]