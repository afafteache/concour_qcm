# C:\Users\HP ElieBook\Downloads\pfe\accounts\decorators.py

from django.shortcuts import redirect
from functools import wraps


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                if request.user.profil.role in roles:
                    return view_func(request, *args, **kwargs)
            except Exception:
                pass
            return redirect('home')
        return wrapper
    return decorator