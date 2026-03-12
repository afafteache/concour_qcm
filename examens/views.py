from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import role_required
from accounts.models import Profil
from concours.models import Concours, Module, SessionConcours
from resultats.models import Resultat
from .models import Examen


# ═══════════════════════════════════════════════════════════════════
#  DASHBOARD ADMIN
# ═══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('admin', 'enseignant')
def dashboard_admin(request):
    now = timezone.now()

    nb_concours  = Concours.objects.count()
    nb_modules   = Module.objects.count()
    nb_candidats = Profil.objects.filter(role='candidat').count()
    nb_sessions  = SessionConcours.objects.count()
    nb_examens   = Examen.objects.count()
    nb_resultats = Resultat.objects.count()

    session_active = (
        SessionConcours.objects
        .filter(etat__in=['planifiee', 'en_cours'])
        .select_related('concours', 'concours__module')
        .order_by('date_heure_debut')
        .first()
    )

    examen_actif = None
    if session_active:
        try:
            examen_actif = session_active.examen
        except Exception:
            pass

    peut_lancer = (
        session_active is not None
        and not session_active.examen_lance
        and now >= session_active.date_heure_debut
    )

    secondes_avant_debut = 0
    if session_active and now < session_active.date_heure_debut:
        secondes_avant_debut = int((session_active.date_heure_debut - now).total_seconds())

    candidats_suivi = []
    if examen_actif:
        try:
            total_q = examen_actif.questions.count()
        except Exception:
            total_q = 0
        for r in Resultat.objects.filter(examen=examen_actif).select_related('candidat', 'candidat__profil'):
            pct = round(r.score / total_q * 100) if total_q > 0 else 0
            candidats_suivi.append({
                'nom'        : r.candidat.get_full_name(),
                'cin'        : r.candidat.profil.cin,
                'score'      : r.score,
                'total'      : total_q,
                'pourcentage': pct,
            })

    context = {
        'nb_concours'          : nb_concours,
        'nb_modules'           : nb_modules,
        'nb_candidats'         : nb_candidats,
        'nb_sessions'          : nb_sessions,
        'nb_examens'           : nb_examens,
        'nb_resultats'         : nb_resultats,
        'session_active'       : session_active,
        'examen_actif'         : examen_actif,
        'peut_lancer'          : peut_lancer,
        'secondes_avant_debut' : secondes_avant_debut,
        'candidats_suivi'      : candidats_suivi,
        'now'                  : now,
    }
    return render(request, 'admin/dashboard_admin.html', context)


# ═══════════════════════════════════════════════════════════════════
#  DASHBOARD CANDIDAT
# ═══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('candidat')
def dashboard_candidat(request):
    now    = timezone.now()
    profil = request.user.profil

    sessions_ouvertes = SessionConcours.objects.filter(
        examen_lance=True,
        date_heure_fin__gte=now,
    )

    examens_disponibles = []
    for s in sessions_ouvertes:
        try:
            examens_disponibles.append(s.examen)
        except Exception:
            pass

    session_prochaine = (
        SessionConcours.objects
        .filter(etat__in=['planifiee', 'en_cours'], date_heure_fin__gte=now)
        .order_by('date_heure_debut')
        .first()
    )

    secondes_avant = 0
    if session_prochaine and not session_prochaine.examen_lance:
        diff = session_prochaine.date_heure_debut - now
        secondes_avant = max(int(diff.total_seconds()), 0)

    mes_resultats      = Resultat.objects.filter(candidat=request.user).select_related('examen').order_by('-date_passage')
    examens_passes_ids = list(mes_resultats.values_list('examen_id', flat=True))

    context = {
        'profil'             : profil,
        'examens_disponibles': examens_disponibles,
        'mes_resultats'      : mes_resultats,
        'examens_passes_ids' : examens_passes_ids,
        'session_prochaine'  : session_prochaine,
        'secondes_avant'     : secondes_avant,
        'now'                : now,
    }
    return render(request, 'candidat/dashboard_candidat.html', context)


# ═══════════════════════════════════════════════════════════════════
#  PASSER UN EXAMEN
# ═══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('candidat')
def examen_view(request, examen_id):
    now    = timezone.now()
    examen = get_object_or_404(Examen, id=examen_id)

    if examen.session:
        if not examen.session.examen_lance:
            messages.error(request, "L'examen n'a pas encore été lancé.")
            return redirect('dashboard_candidat')
        if now > examen.session.date_heure_fin:
            messages.error(request, "Le temps de cet examen est écoulé.")
            return redirect('dashboard_candidat')

    if Resultat.objects.filter(candidat=request.user, examen=examen).exists():
        return redirect('resultat', examen_id=examen_id)

    try:
        questions = examen.questions.prefetch_related('choix_set').all()
    except Exception:
        questions = []

    if request.method == 'POST':
        score = 0
        for question in questions:
            reponse_id = request.POST.get(f'question_{question.id}')
            if reponse_id:
                try:
                    choix = question.choix_set.get(id=int(reponse_id))
                    if choix.est_correct:
                        score += 1
                except Exception:
                    pass
        Resultat.objects.create(candidat=request.user, examen=examen, score=score)
        return redirect('resultat', examen_id=examen_id)

    if examen.session:
        duree_restante = max(int((examen.session.date_heure_fin - now).total_seconds()), 0)
    else:
        duree_restante = 3600

    return render(request, 'candidat/examen.html', {
        'examen'        : examen,
        'questions'     : questions,
        'duree_restante': duree_restante,
    })


# ═══════════════════════════════════════════════════════════════════
#  RÉSULTAT CANDIDAT
# ═══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('candidat')
def resultat_view(request, examen_id):
    examen   = get_object_or_404(Examen, id=examen_id)
    resultat = get_object_or_404(Resultat, candidat=request.user, examen=examen)
    try:
        total = examen.questions.count()
    except Exception:
        total = 0
    pourcentage = round((resultat.score / total * 100), 1) if total > 0 else 0

    return render(request, 'candidat/resultat.html', {
        'examen'     : examen,
        'resultat'   : resultat,
        'total'      : total,
        'pourcentage': pourcentage,
        'reussi'     : pourcentage >= 50,
    })