from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('login/candidat/', views.login_candidat_view, name='login_candidat'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]