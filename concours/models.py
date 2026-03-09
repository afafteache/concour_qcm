from django.db import models


class Module(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Concours(models.Model):
    titre = models.CharField(max_length=200)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    date = models.DateField()
    duree_minutes = models.PositiveIntegerField()
    nombre_questions = models.PositiveIntegerField()

    def __str__(self):
        return self.titre


class SessionConcours(models.Model):
    concours = models.ForeignKey(Concours, on_delete=models.CASCADE)
    nom_session = models.CharField(max_length=100)
    date_heure_debut = models.DateTimeField()
    date_heure_fin = models.DateTimeField()

    def __str__(self):
        return f"{self.concours.titre} - {self.nom_session}"