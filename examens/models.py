from django.db import models
from django.contrib.auth.models import User
from concours.models import SessionConcours


class Examen(models.Model):
    STATUT_CHOICES = [
        ('brouillon',   'Brouillon'),
        ('envoye',      'Envoyé à l\'admin'),
        ('valide',      'Validé par l\'admin'),
    ]

    titre         = models.CharField(max_length=200)
    session       = models.OneToOneField(
        SessionConcours, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='examen'
    )
    questions     = models.ManyToManyField(
        'questions.Question',
        blank=True,
        related_name='examens'
    )
    date          = models.DateTimeField(auto_now_add=True)
    actif         = models.BooleanField(default=False)
    statut        = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    cree_par      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='examens_crees'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-date_creation']