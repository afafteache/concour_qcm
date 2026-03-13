from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Profil
from .decorators import role_required


def get_profil(user):
    """Récupère le profil lié à l'utilisateur."""
    return Profil.objects.filter(user=user).first()


def redirect_role(user):
    """Redirige vers le bon dashboard selon le rôle."""
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
    return redirect('login')


def login_view(request):
    """Connexion admin / enseignant avec CIN + mot de passe."""
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
    """Connexion candidat avec nom complet + CIN."""
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


@login_required(login_url='login')
def dashboard_admin(request):
    from concours.models import SessionConcours, Concours
    from resultats.models import Resultat

    profil = get_profil(request.user)
    if profil is None or profil.role != 'admin':
        logout(request)
        return redirect('login')

    sessions = SessionConcours.objects.select_related('concours').order_by('-id')
    concours_list = Concours.objects.all()
    nb_candidats = Profil.objects.filter(role='candidat').count()
    nb_resultats = Resultat.objects.count()

    return render(request, 'admin/dashboard_admin.html', {
        'sessions': sessions,
        'concours_list': concours_list,
        'nb_candidats': nb_candidats,
        'nb_resultats': nb_resultats,
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
    examens = Examen.objects.all()
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

    # Tous les examens actifs
    examens_disponibles = Examen.objects.filter(actif=True).select_related('session').order_by('-date')

    # IDs des examens déjà passés par le candidat
    examens_passes_ids = list(
        Resultat.objects.filter(candidat=request.user).values_list('examen_id', flat=True)
    )

    # Résultats personnels du candidat
    mes_resultats = Resultat.objects.filter(candidat=request.user).select_related('examen').order_by('-id')

    # Prochaine session non encore lancée
    session_prochaine = SessionConcours.objects.filter(
        date_heure_debut__gt=maintenant
    ).select_related('concours').order_by('date_heure_debut').first()

    # Calcul du temps restant avant la prochaine session
    secondes_avant = 0
    if session_prochaine:
        diff = session_prochaine.date_heure_debut - maintenant
        secondes_avant = max(int(diff.total_seconds()), 0)

    return render(request, 'candidat/dashboard_candidat.html', {
        'profil': profil,
        'examens_disponibles': examens_disponibles,
        'examens_passes_ids': examens_passes_ids,
        'session_prochaine': session_prochaine,
        'mes_resultats': mes_resultats,
        'secondes_avant': secondes_avant,
    })


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def register_view(request):
    current_profil = get_profil(request.user)

    if current_profil is None:
        logout(request)
        return redirect('login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        cin = request.POST.get('cin', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        role = request.POST.get('role', 'candidat').strip()

        if not first_name or not last_name or not cin:
            messages.error(request, 'Prénom, nom et CIN sont obligatoires.')

        elif Profil.objects.filter(cin=cin).exists():
            messages.error(request, 'Ce CIN est déjà utilisé.')

        elif role in ['admin', 'enseignant'] and current_profil.role != 'admin':
            messages.error(request, 'Seul un administrateur peut créer ce type de compte.')

        elif role in ['admin', 'enseignant'] and not password:
            messages.error(request, 'Un mot de passe est obligatoire.')

        elif role in ['admin', 'enseignant'] and password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')

        else:
            if role == 'candidat':
                user = User.objects.create_user(
                    username=cin,
                    email=email,
                    password=User.objects.make_random_password(),
                    first_name=first_name,
                    last_name=last_name
                )
            else:
                user = User.objects.create_user(
                    username=cin,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                if role == 'admin':
                    user.is_staff = True
                    user.save()

            Profil.objects.create(user=user, cin=cin, role=role)
            messages.success(request, f'Compte de {first_name} {last_name} créé avec succès.')

            if current_profil.role == 'admin':
                return redirect('dashboard_admin')
            return redirect('dashboard_enseignant')

    roles_disponibles = ['admin', 'enseignant', 'candidat'] if current_profil.role == 'admin' else ['candidat']

    return render(request, 'register.html', {
        'roles_disponibles': roles_disponibles
    })