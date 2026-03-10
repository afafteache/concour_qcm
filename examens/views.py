from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Examen

@login_required
def dashboard_candidat(request):
    examens = Examen.objects.all()
    return render(request, "candidat/dashboard.html", {"examens": examens})


@login_required
def passer_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    questions = examen.questions.all()

    return render(request, "candidat/examen.html", {
        "examen": examen,
        "questions": questions
    })
