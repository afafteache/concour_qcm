from django.db import models

class Question(models.Model):
    texte = models.CharField(max_length=255)

    def __str__(self):
        return self.texte


class Choix(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choix")
    texte = models.CharField(max_length=200)
    est_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.texte
