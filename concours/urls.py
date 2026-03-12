from django.urls import path
from . import views

urlpatterns = [
    path('modules/',                    views.module_liste,     name='module_liste'),
    path('modules/creer/',              views.module_creer,     name='module_creer'),
    path('modules/<int:pk>/modifier/',  views.module_modifier,  name='module_modifier'),
    path('modules/<int:pk>/supprimer/', views.module_supprimer, name='module_supprimer'),

    path('concours/',                    views.concours_liste,     name='concours_liste'),
    path('concours/creer/',              views.concours_creer,     name='concours_creer'),
    path('concours/<int:pk>/modifier/',  views.concours_modifier,  name='concours_modifier'),
    path('concours/<int:pk>/supprimer/', views.concours_supprimer, name='concours_supprimer'),

    path('sessions/',                    views.session_liste,     name='session_liste'),
    path('sessions/creer/',              views.session_creer,     name='session_creer'),
    path('sessions/<int:pk>/modifier/',  views.session_modifier,  name='session_modifier'),
    path('sessions/<int:pk>/supprimer/', views.session_supprimer, name='session_supprimer'),
    path('sessions/<int:pk>/lancer/',    views.session_lancer,    name='session_lancer'),
]