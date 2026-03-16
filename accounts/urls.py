from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),

    # Connexions
    path('login/', views.login_view, name='login'),
    path('login/candidat/', views.login_candidat_view, name='login_candidat'),

    # Déconnexion
    path('logout/', views.logout_view, name='logout'),

    # Inscription
    path('register/', views.register_view, name='register'),

    # Dashboards
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('enseignant/dashboard/', views.dashboard_enseignant, name='dashboard_enseignant'),
    path('candidat/dashboard/', views.dashboard_candidat, name='dashboard_candidat'),
]