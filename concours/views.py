from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard_admin')
        else:
            return render(request, 'login.html', {
                'error': "Nom d'utilisateur ou mot de passe incorrect."
            })

    return render(request, 'login.html')

def dashboard_admin(request):
    return render(request, 'dashboard_admin.html')