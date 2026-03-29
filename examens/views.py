from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import role_required
from accounts.models import Profil
from concours.models import Concours, Module, SessionConcours
from resultats.models import Resultat
from .models import Examen, ExamenEnCours


def get_profil(user):
    return Profil.objects.filter(user=user).first()


# ═══════════════════════════════════════════════════════
#  DASHBOARD ADMIN
# ═══════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('admin', 'enseignant')
def dashboard_admin(request):
    now = timezone.now()
    nb_concours  = Concours.objects.count()
    nb_candidats = Profil.objects.filter(role='candidat').count()
    nb_sessions  = SessionConcours.objects.count()
    nb_resultats = Resultat.objects.count()

    session_active = (
        SessionConcours.objects
        .filter(etat__in=['planifiee', 'en_cours'])
        .select_related('concours')
        .order_by('-date_heure_debut')
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

        # Candidats ayant soumis
        soumis_ids = []
        for r in Resultat.objects.filter(examen=examen_actif).select_related('candidat'):
            pct = round(r.score / total_q * 100) if total_q > 0 else 0
            profil_c = get_profil(r.candidat)
            cin = profil_c.cin if profil_c else '—'
            soumis_ids.append(cin)
            candidats_suivi.append({
                'nom'        : r.candidat.get_full_name(),
                'cin'        : cin,
                'score'      : r.score,
                'total'      : total_q,
                'pourcentage': pct,
                'statut'     : 'soumis',
            })

        # Candidats en cours
        for ec in ExamenEnCours.objects.filter(examen=examen_actif).select_related('candidat'):
            try:
                profil_c = get_profil(ec.candidat)
                cin = profil_c.cin if profil_c else '—'
                if cin not in soumis_ids:
                    candidats_suivi.append({
                        'nom'        : ec.candidat.get_full_name(),
                        'cin'        : cin,
                        'score'      : '—',
                        'total'      : total_q,
                        'pourcentage': 0,
                        'statut'     : 'en_cours',
                    })
            except Exception:
                pass

    return render(request, 'admin/dashboard_admin.html', {
        'nb_concours'         : nb_concours,
        'nb_candidats'        : nb_candidats,
        'nb_sessions'         : nb_sessions,
        'nb_resultats'        : nb_resultats,
        'session_active'      : session_active,
        'examen_actif'        : examen_actif,
        'peut_lancer'         : peut_lancer,
        'secondes_avant_debut': secondes_avant_debut,
        'candidats_suivi'     : candidats_suivi,
        'now'                 : now,
    })


# ═══════════════════════════════════════════════════════
#  ADMIN — GESTION EXAMENS
# ═══════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('admin')
def admin_examens(request):
    examens = Examen.objects.select_related('cree_par').prefetch_related('questions').order_by('-date_creation')
    nb_nouveaux = examens.filter(statut='envoye').count()
    return render(request, 'admin/examens/liste.html', {
        'examens'    : examens,
        'nb_nouveaux': nb_nouveaux,
    })


@login_required(login_url='login')
@role_required('admin')
def admin_valider_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    if request.method == 'POST':
        examen.statut = 'valide'
        examen.actif  = True
        examen.save()
        messages.success(request, f'L\'examen "{examen.titre}" a été validé.')
    return redirect('admin_examens')


@login_required(login_url='login')
@role_required('admin')
def creer_session_pour_examen(request, examen_id):
    examen        = get_object_or_404(Examen, id=examen_id, statut='valide')
    concours_list = Concours.objects.all()

    if request.method == 'POST':
        nom_session = request.POST.get('nom_session', '').strip()
        concours_id = request.POST.get('concours')
        date_debut  = request.POST.get('date_heure_debut')
        date_fin    = request.POST.get('date_heure_fin')
        duree       = request.POST.get('duree_minutes', 60)

        if not nom_session or not concours_id or not date_debut or not date_fin:
            messages.error(request, 'Veuillez remplir tous les champs.')
        else:
            try:
                concours = Concours.objects.get(id=concours_id)
                session  = SessionConcours.objects.create(
                    nom_session      = nom_session,
                    concours         = concours,
                    date_heure_debut = date_debut,
                    date_heure_fin   = date_fin,
                    duree_minutes    = int(duree),
                    etat             = 'planifiee',
                    lance_par        = request.user,
                )
                examen.session = session
                examen.save()
                messages.success(request, f'Session "{nom_session}" créée et liée à l\'examen.')
                return redirect('admin_examens')
            except Exception as e:
                messages.error(request, f'Erreur : {e}')

    return render(request, 'admin/sessions/creer_pour_examen.html', {
        'examen'       : examen,
        'concours_list': concours_list,
    })


@login_required(login_url='login')
@role_required('admin')
def admin_confirmer_suppression_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    return render(request, 'admin/examens/confirmer_suppression.html', {'examen': examen})


# ═══════════════════════════════════════════════════════
#  DASHBOARD CANDIDAT
# ═══════════════════════════════════════════════════════

@login_required(login_url='login_candidat')
@role_required('candidat')
def dashboard_candidat(request):
    now    = timezone.now()
    profil = get_profil(request.user)

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

    return render(request, 'candidat/dashboard_candidat.html', {
        'profil'             : profil,
        'examens_disponibles': examens_disponibles,
        'mes_resultats'      : mes_resultats,
        'examens_passes_ids' : examens_passes_ids,
        'session_prochaine'  : session_prochaine,
        'secondes_avant'     : secondes_avant,
        'now'                : now,
    })


# ═══════════════════════════════════════════════════════
#  PASSER UN EXAMEN
# ═══════════════════════════════════════════════════════

@login_required(login_url='login_candidat')
@role_required('candidat')
def examen_view(request, examen_id):
    now    = timezone.now()
    examen = get_object_or_404(Examen, id=examen_id)
    session = examen.session if examen.session_id else None

    if session:
        if not session.examen_lance:
            messages.error(request, "L'examen n'a pas encore été lancé.")
            return redirect('dashboard_candidat')
        if now > session.date_heure_fin:
            messages.error(request, "Le temps de cet examen est écoulé.")
            return redirect('dashboard_candidat')

    if Resultat.objects.filter(candidat=request.user, examen=examen).exists():
        return redirect('resultat', examen_id=examen_id)

    # Enregistre que le candidat a ouvert l'examen
    ExamenEnCours.objects.get_or_create(candidat=request.user, examen=examen)

    questions = examen.questions.prefetch_related('choix_set').all()

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
        ExamenEnCours.objects.filter(candidat=request.user, examen=examen).delete()
        return redirect('resultat', examen_id=examen_id)

    if session:
        duree_restante = max(int((session.date_heure_fin - now).total_seconds()), 0)
    else:
        duree_restante = 3600

    return render(request, 'candidat/examen.html', {
        'examen'        : examen,
        'questions'     : questions,
        'duree_restante': duree_restante,
    })


# ═══════════════════════════════════════════════════════
#  RÉSULTAT CANDIDAT
# ═══════════════════════════════════════════════════════

@login_required(login_url='login_candidat')
@role_required('candidat')
def resultat_view(request, examen_id):
    examen      = get_object_or_404(Examen, id=examen_id)
    resultat    = get_object_or_404(Resultat, candidat=request.user, examen=examen)
    total       = examen.questions.count()
    pourcentage = round((resultat.score / total * 100), 1) if total > 0 else 0

    return render(request, 'candidat/resultat.html', {
        'examen'     : examen,
        'resultat'   : resultat,
        'total'      : total,
        'pourcentage': pourcentage,
        'reussi'     : pourcentage >= 50,
    })


# ═══════════════════════════════════════════════════════
#  DASHBOARD ENSEIGNANT
# ═══════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('enseignant')
def dashboard_enseignant(request):
    from questions.models import Question
    questions    = Question.objects.filter(cree_par=request.user).select_related('module').order_by('-date_creation')
    nb_questions = questions.count()
    examens      = Examen.objects.filter(cree_par=request.user)

    return render(request, 'enseignant/dashboard_enseignant.html', {
        'questions'   : questions,
        'nb_questions': nb_questions,
        'examens'     : examens,
    })


# ═══════════════════════════════════════════════════════
#  SUPPRIMER EXAMEN — ADMIN
# ═══════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('admin')
def admin_supprimer_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    if request.method == 'POST':
        titre = examen.titre
        examen.delete()
        messages.success(request, f'Examen "{titre}" supprimé avec succès.')
    return redirect('admin_examens')


# ═══════════════════════════════════════════════════════
#  CONFIRMER SUPPRESSION EXAMEN — ENSEIGNANT
# ═══════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('enseignant')
def enseignant_confirmer_suppression_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id, cree_par=request.user)
    return render(request, 'enseignant/examens/confirmer_suppression.html', {'examen': examen})


# ═══════════════════════════════════════════════════════
#  SUPPRIMER EXAMEN — ENSEIGNANT
# ═══════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('enseignant')
def enseignant_supprimer_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id, cree_par=request.user)
    if request.method == 'POST':
        titre = examen.titre
        examen.delete()
        messages.success(request, f'Examen "{titre}" supprimé avec succès.')
    return redirect('mes_examens')