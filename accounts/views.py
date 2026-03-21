from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Profil
from .decorators import role_required


def get_profil(user):
    return Profil.objects.filter(user=user).first()


def redirect_role(user):
    profil = get_profil(user)
    if profil is None:
        return redirect('login')
    if profil.role == 'admin':
        return redirect('dashboard_admin')
    elif profil.role == 'enseignant':
        return redirect('dashboard_enseignant')
    elif profil.role == 'candidat':
        return redirect('dashboard_candidat')
    return redirect('login')


def home(request):
    if request.user.is_authenticated:
        return redirect_role(request.user)
    return render(request, 'home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect_role(request.user)
    if request.method == 'POST':
        cin = request.POST.get('cin', '').strip()
        password = request.POST.get('password', '').strip()
        try:
            profil = Profil.objects.select_related('user').get(cin=cin)
            if profil.role == 'candidat':
                messages.error(request, "Utilisez la page de connexion candidat.")
            elif profil.user.check_password(password):
                login(request, profil.user)
                return redirect_role(profil.user)
            else:
                messages.error(request, "CIN ou mot de passe incorrect.")
        except Profil.DoesNotExist:
            messages.error(request, "CIN ou mot de passe incorrect.")
    return render(request, 'login.html')


def login_candidat_view(request):
    if request.user.is_authenticated:
        return redirect_role(request.user)
    if request.method == 'POST':
        nom_complet = request.POST.get('nom_complet', '').strip()
        cin = request.POST.get('cin', '').strip()
        if not nom_complet or not cin:
            messages.error(request, "Veuillez remplir tous les champs.")
        else:
            try:
                profil = Profil.objects.select_related('user').get(cin=cin, role='candidat')
                user = profil.user
                nom_db = f"{user.first_name} {user.last_name}".strip().lower()
                if nom_db == nom_complet.lower():
                    login(request, user)
                    return redirect('dashboard_candidat')
                else:
                    messages.error(request, "Nom complet ou CIN incorrect.")
            except Profil.DoesNotExist:
                messages.error(request, "Nom complet ou CIN incorrect.")
    return render(request, 'candidat/login_candidat.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_public_view(request):
    """Inscription publique — admin uniquement."""
    if request.user.is_authenticated:
        return redirect_role(request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        cin        = request.POST.get('cin', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '').strip()
        password2  = request.POST.get('password2', '').strip()

        if not first_name or not last_name or not cin:
            messages.error(request, 'Prénom, nom et CIN sont obligatoires.')
        elif Profil.objects.filter(cin=cin).exists():
            messages.error(request, 'Ce CIN est déjà utilisé.')
        elif not password:
            messages.error(request, 'Le mot de passe est obligatoire.')
        elif password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif len(password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
        else:
            user = User.objects.create_user(
                username=cin, email=email, password=password,
                first_name=first_name, last_name=last_name
            )
            user.is_staff = True
            user.save()
            Profil.objects.create(user=user, cin=cin, role='admin')
            messages.success(request, 'Compte administrateur créé ! Connectez-vous.')
            return redirect('login')

    return render(request, 'register_public.html')


@login_required(login_url='login')
def dashboard_admin(request):
    from concours.models import SessionConcours, Concours
    from resultats.models import Resultat
    from examens.models import Examen

    profil = get_profil(request.user)
    if profil is None or profil.role != 'admin':
        logout(request)
        return redirect('login')

    sessions = SessionConcours.objects.select_related('concours').order_by('-id')
    concours_list = Concours.objects.all()
    nb_candidats = Profil.objects.filter(role='candidat').count()
    nb_resultats = Resultat.objects.count()
    nb_examens_nouveaux = Examen.objects.filter(statut='envoye').count()

    now = timezone.now()
    session_active = SessionConcours.objects.filter(
        etat__in=['planifiee', 'en_cours'],
        date_heure_fin__gte=now
    ).select_related('concours').order_by('date_heure_debut').first()

    peut_lancer = False
    secondes_avant_debut = 0
    candidats_suivi = []
    examen_actif = None

    if session_active:
        try:
            examen_actif = session_active.examen
        except Exception:
            pass
        peut_lancer = (
            not session_active.examen_lance
            and now >= session_active.date_heure_debut
        )
        if now < session_active.date_heure_debut:
            secondes_avant_debut = int((session_active.date_heure_debut - now).total_seconds())
        if examen_actif:
            total_q = examen_actif.questions.count()
            for r in Resultat.objects.filter(examen=examen_actif).select_related('candidat'):
                pct = round(r.score / total_q * 100) if total_q > 0 else 0
                profil_c = get_profil(r.candidat)
                candidats_suivi.append({
                    'nom': r.candidat.get_full_name(),
                    'cin': profil_c.cin if profil_c else '—',
                    'score': r.score,
                    'total': total_q,
                    'pourcentage': pct,
                })

    return render(request, 'admin/dashboard_admin.html', {
        'sessions': sessions,
        'concours_list': concours_list,
        'nb_candidats': nb_candidats,
        'nb_resultats': nb_resultats,
        'nb_examens_nouveaux': nb_examens_nouveaux,
        'session_active': session_active,
        'examen_actif': examen_actif,
        'peut_lancer': peut_lancer,
        'secondes_avant_debut': secondes_avant_debut,
        'candidats_suivi': candidats_suivi,
        'now': now,
    })


@login_required(login_url='login')
def dashboard_enseignant(request):
    from questions.models import Question
    from examens.models import Examen

    profil = get_profil(request.user)
    if profil is None or profil.role != 'enseignant':
        logout(request)
        return redirect('login')

    questions = Question.objects.filter(cree_par=request.user).order_by('-date_creation')
    examens = Examen.objects.filter(cree_par=request.user)
    nb_questions = questions.count()

    return render(request, 'enseignant/dashboard_enseignant.html', {
        'questions': questions,
        'examens': examens,
        'nb_questions': nb_questions,
    })


@login_required(login_url='login_candidat')
def dashboard_candidat(request):
    from concours.models import SessionConcours
    from resultats.models import Resultat
    from examens.models import Examen

    profil = get_profil(request.user)
    if profil is None or profil.role != 'candidat':
        logout(request)
        return redirect('login_candidat')

    maintenant = timezone.now()
    tolerance = timedelta(minutes=5)

    sessions_lancees = SessionConcours.objects.filter(
        examen_lance=True,
        date_heure_fin__gte=maintenant
    )

    examens_disponibles = []
    examens_en_retard = []

    for s in sessions_lancees:
        try:
            if s.examen and s.examen.actif:
                limite = s.date_heure_debut + tolerance
                if maintenant <= limite:
                    examens_disponibles.append(s.examen)
                else:
                    examens_en_retard.append(s.examen)
        except Exception:
            pass

    examens_passes_ids = list(
        Resultat.objects.filter(candidat=request.user).values_list('examen_id', flat=True)
    )

    # Session encore active ?
    session_encore_active = SessionConcours.objects.filter(
        examen_lance=True,
        date_heure_fin__gte=maintenant
    ).exists()

    mes_resultats = Resultat.objects.filter(
        candidat=request.user
    ).select_related('examen').order_by('-id')

    session_prochaine = SessionConcours.objects.filter(
        date_heure_fin__gte=maintenant,
        examen_lance=False
    ).order_by('date_heure_debut').first()

    secondes_avant = 0
    if session_prochaine:
        diff = session_prochaine.date_heure_debut - maintenant
        secondes_avant = max(int(diff.total_seconds()), 0)

    return render(request, 'candidat/dashboard_candidat.html', {
        'profil': profil,
        'examens_disponibles': examens_disponibles,
        'examens_en_retard': examens_en_retard,
        'examens_passes_ids': examens_passes_ids,
        'session_encore_active': session_encore_active,
        'session_prochaine': session_prochaine,
        'mes_resultats': mes_resultats,
        'secondes_avant': secondes_avant,
    })


@login_required(login_url='login')
@role_required('admin')
def register_view(request):
    current_profil = get_profil(request.user)
    if current_profil is None:
        logout(request)
        return redirect('login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        cin        = request.POST.get('cin', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '').strip()
        password2  = request.POST.get('password2', '').strip()
        role       = request.POST.get('role', 'candidat').strip()

        if not first_name or not last_name or not cin:
            messages.error(request, 'Prénom, nom et CIN sont obligatoires.')
        elif Profil.objects.filter(cin=cin).exists():
            messages.error(request, 'Ce CIN est déjà utilisé.')
        elif role not in ['candidat', 'enseignant']:
            messages.error(request, 'Rôle invalide.')
        elif role == 'enseignant' and not password:
            messages.error(request, 'Un mot de passe est obligatoire pour l\'enseignant.')
        elif role == 'enseignant' and password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        else:
            if role == 'candidat':
                user = User.objects.create_user(
                    username=cin, email=email,
                    password=User.objects.make_random_password(),
                    first_name=first_name, last_name=last_name
                )
            else:
                user = User.objects.create_user(
                    username=cin, email=email, password=password,
                    first_name=first_name, last_name=last_name
                )
            Profil.objects.create(user=user, cin=cin, role=role)
            messages.success(request, f'Compte de {first_name} {last_name} créé avec succès.')
            return redirect('dashboard_admin')

    return render(request, 'admin/register.html', {})