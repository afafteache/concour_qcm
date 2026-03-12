from django.db import models
from concours.models import Module


class Question(models.Model):
    texte    = models.TextField()
    module   = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    cree_par = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='questions_creees'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.texte[:80]

    class Meta:
        verbose_name        = 'Question'
        verbose_name_plural = 'Questions'


class Choix(models.Model):
    question    = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix_set')
    texte       = models.CharField(max_length=300)
    est_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✔' if self.est_correct else '✘'} {self.texte[:60]}"

    class Meta:
        verbose_name        = 'Choix'
        verbose_name_plural = 'Choix'