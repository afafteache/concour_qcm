# C:\Users\HP ElieBook\Downloads\pfe\resultats\models.py

from django.db import models
from django.contrib.auth.models import User
from examens.models import Examen


class Resultat(models.Model):
    candidat     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resultats')
    examen       = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='resultats')
    score        = models.PositiveIntegerField(default=0)
    date_passage = models.DateTimeField(auto_now_add=True)

    def total_questions(self):
        try:
            return self.examen.questions.count()
        except Exception:
            return 0

    def pourcentage(self):
        total = self.total_questions()
        return round((self.score / total * 100), 1) if total > 0 else 0

    def reussi(self):
        return self.pourcentage() >= 50

    def __str__(self):
        return f"{self.candidat.get_full_name()} — {self.examen.titre} — {self.score}"

    class Meta:
        unique_together = ('candidat', 'examen')
        ordering        = ['-date_passage']