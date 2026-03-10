from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # concours
    path('', include('concours.urls')),

    # examens
    path('examens/', include('examens.urls')),

    # resultats
    path('resultats/', include('resultats.urls')),
]
