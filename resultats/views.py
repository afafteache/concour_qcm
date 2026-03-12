# C:\Users\HP ElieBook\Downloads\pfe\resultats\views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from examens.models import Examen
from .models import Resultat


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def resultats_liste(request):
    resultats = Resultat.objects.select_related(
        'candidat', 'candidat__profil', 'examen'
    ).all()
    examen_id = request.GET.get('examen')
    if examen_id:
        resultats = resultats.filter(examen_id=examen_id)
    examens = Examen.objects.all()
    return render(request, 'admin/resultats/liste.html', {
        'resultats'          : resultats,
        'examens'            : examens,
        'examen_selectionne' : examen_id,
    })