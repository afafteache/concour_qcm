from django.shortcuts import redirect
from functools import wraps
from .models import Profil


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if 'candidat' in roles and len(roles) == 1:
                    return redirect('login_candidat')
                return redirect('login')

            # Utiliser Profil.objects.filter au lieu de user.profil
            profil = Profil.objects.filter(user=request.user).first()

            if profil is None:
                return redirect('login')

            if profil.role in roles:
                return view_func(request, *args, **kwargs)

            # Mauvais rôle → rediriger vers son propre dashboard
            if profil.role == 'admin':
                return redirect('dashboard_admin')
            if profil.role == 'enseignant':
                return redirect('dashboard_enseignant')
            if profil.role == 'candidat':
                return redirect('dashboard_candidat')

            return redirect('login')
        return wrapper
    return decorator