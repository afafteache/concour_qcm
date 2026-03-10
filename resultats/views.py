from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Resultat

@login_required
def resultat(request):
    resultats = Resultat.objects.filter(candidat=request.user)

    return render(request, "candidat/resultat.html", {
        "resultats": resultats
    })
