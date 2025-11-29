# admin_dashboard/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.shortcuts import redirect


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Versuchen, den Benutzer zu authentifizieren
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Wenn der Benutzer existiert, logge ihn ein und leite zum Dashboard weiter
            login(request, user)
            return redirect('dashboard_home')
        else:
            # Fehler, falls der Benutzername oder das Passwort falsch sind
            return render(request, 'admin_dashboard/login.html', {
                'error_message': 'Benutzername oder Passwort ist ungültig.'
            })
    return render(request, 'admin_dashboard/login.html')

@login_required
def dashboard_home(request):
    return render(request, 'admin_dashboard/dashboard_home.html')

def logout_view(request):
    logout(request)
    return redirect('login')


