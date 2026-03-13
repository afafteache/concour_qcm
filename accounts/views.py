from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profil
from .decorators import role_required


def home(request):
    if request.user.is_authenticated:
        return redirect_role(request.user)
    return redirect('login')


def login_view(request):
    """Connexion pour admin et enseignant : CIN + mot de passe."""
    
    if request.user.is_authenticated:
        return redirect_role(request.user)

    if request.method == 'POST':
        cin = request.POST.get('cin', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            profil = Profil.objects.select_related('user').get(cin=cin)

            if profil.role == 'candidat':
                messages.error(request, 'Utilisez la page de connexion candidat.')
            
            elif profil.user.check_password(password):
                login(request, profil.user)
                return redirect_role(profil.user)

            else:
                messages.error(request, 'CIN ou mot de passe incorrect.')

        except Profil.DoesNotExist:
            messages.error(request, 'CIN ou mot de passe incorrect.')

    return render(request, 'login.html')


def login_candidat_view(request):
    """Connexion candidat : nom complet + CIN."""

    if request.user.is_authenticated:
        return redirect_role(request.user)

    if request.method == 'POST':
        nom_complet = request.POST.get('nom_complet', '').strip()
        cin = request.POST.get('cin', '').strip()

        if not nom_complet or not cin:
            messages.error(request, 'Veuillez remplir tous les champs.')

        else:
            try:
                profil = Profil.objects.select_related('user').get(cin=cin, role='candidat')
                user = profil.user

                nom_db = f"{user.first_name} {user.last_name}".strip().lower()

                if nom_db == nom_complet.lower():
                    login(request, user)
                    return redirect('dashboard_candidat')

                else:
                    messages.error(request, 'Nom complet ou CIN incorrect.')

            except Profil.DoesNotExist:
                messages.error(request, 'Nom complet ou CIN incorrect.')

    return render(request, 'candidat/login_candidat.html')


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def register_view(request):
    """
    Création de compte :
    - Admin peut créer : admin, enseignant, candidat
    - Enseignant peut créer : candidat uniquement
    """

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

        elif role in ['admin', 'enseignant'] and request.user.profil.role != 'admin':
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

            Profil.objects.create(
                user=user,
                cin=cin,
                role=role
            )

            messages.success(request, f'Compte de {first_name} {last_name} créé avec succès.')

            if request.user.profil.role == 'admin':
                return redirect('dashboard_admin')

            return redirect('dashboard_enseignant')

    if request.user.profil.role == 'admin':
        roles_disponibles = ['admin', 'enseignant', 'candidat']
    else:
        roles_disponibles = ['candidat']

    return render(request, 'register.html', {
        'roles_disponibles': roles_disponibles
    })


def logout_view(request):
    logout(request)
    return redirect('login')


def redirect_role(user):
    """Redirige vers le bon dashboard."""

    try:
        role = user.profil.role
    except:
        return redirect('login')

    if role == 'admin':
        return redirect('dashboard_admin')

    if role == 'enseignant':
        return redirect('dashboard_enseignant')

    return redirect('dashboard_candidat')