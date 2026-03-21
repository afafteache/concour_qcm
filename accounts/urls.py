from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('login/candidat/', views.login_candidat_view, name='login_candidat'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),           # Admin connecté crée candidats
    path('inscription/', views.register_public_view, name='register_public'),  # Inscription publique
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('enseignant/dashboard/', views.dashboard_enseignant, name='dashboard_enseignant'),
    path('candidat/dashboard/', views.dashboard_candidat, name='dashboard_candidat'),
]