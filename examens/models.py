from django.db import models
from questions.models import Question

class Examen(models.Model):
    titre = models.CharField(max_length=200)
    date = models.DateTimeField()
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.titre
