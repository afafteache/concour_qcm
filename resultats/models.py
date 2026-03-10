from django.db import models
from django.contrib.auth.models import User
from examens.models import Examen

class Resultat(models.Model):
    candidat = models.ForeignKey(User, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.candidat.username} - {self.score}"
