# admin_dashboard/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Versuchen, den Benutzer zu authentifizieren
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Wenn der Benutzer existiert, logge ihn ein und leite zum Dashboard weiter
            login(request, user)
            return redirect('dashboard_home')
        error_message = 'Benutzername oder Passwort ist ungültig.'
    else:
        error_message = None

    return render(request, 'admin_dashboard/login.html', {'error_message': error_message})

@login_required
def dashboard_home(request):
    return render(request, 'admin_dashboard/dashboard_home.html')

def logout_view(request):
    logout(request)
    return redirect('login')


