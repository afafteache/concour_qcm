from django.db import models
from django.contrib.auth.models import User


class Module(models.Model):
    nom         = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


class Concours(models.Model):
    titre            = models.CharField(max_length=200)
    description      = models.TextField(blank=True)
    date             = models.DateField()
    module           = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='concours')
    nombre_questions = models.PositiveIntegerField(default=20)
    duree_minutes    = models.PositiveIntegerField(default=60)
    cree_par         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='concours_crees')
    date_creation    = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-date']


class SessionConcours(models.Model):
    ETAT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours',  'En cours'),
        ('terminee',  'Terminée'),
        ('annulee',   'Annulée'),
    ]
    nom_session      = models.CharField(max_length=200)
    concours         = models.ForeignKey(Concours, on_delete=models.CASCADE, related_name='sessions')
    date_heure_debut = models.DateTimeField()
    date_heure_fin   = models.DateTimeField()
    duree_minutes    = models.PositiveIntegerField(default=60)
    etat             = models.CharField(max_length=20, choices=ETAT_CHOICES, default='planifiee')
    examen_lance     = models.BooleanField(default=False)
    date_lancement   = models.DateTimeField(null=True, blank=True)
    lance_par        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions_lancees')

    # PAS de champ examen ici — la relation est définie dans examens.Examen.session

    def __str__(self):
        return f"{self.nom_session} — {self.concours.titre}"

    class Meta:
        ordering = ['-date_heure_debut']