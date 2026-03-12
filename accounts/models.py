from django.db import models
from django.contrib.auth.models import User


class Profil(models.Model):
    ROLE_CHOICES = [
        ('admin',      'Administrateur'),
        ('enseignant', 'Enseignant'),
        ('candidat',   'Candidat'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    cin  = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidat')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()}) — {self.cin}"