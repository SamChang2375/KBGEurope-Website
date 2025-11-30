from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import PageVisit # Importieren!


from pages.models import CateringRequest, ContactRequest, SiteImage
from .models import UserProfile  # wichtig

User = get_user_model()
def login_view(request):
    """
    Einfaches Login-View für das interne Dashboard.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Profil holen/erstellen
            profile, _ = UserProfile.objects.get_or_create(user=user)

            # Muss Passwort ändern? -> sofort auf eigene Seite leiten
            if profile.must_change_password:
                return redirect("force_password_change")

            return redirect("dashboard_home")
        else:
            messages.error(request, "Benutzername oder Passwort ist falsch.")

    return render(request, "admin_dashboard/login.html")


@login_required
def dashboard_home(request):
    # ... (Anfragen laden und Bilder laden bleibt gleich) ...

    # 3. STATISTIKEN BERECHNEN
    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    visits_qs = PageVisit.objects.filter(timestamp__gte=last_30_days)

    # Basis-Stats
    total_visits = visits_qs.count()
    unique_visitors = visits_qs.values('session_key').distinct().count()
    today_visits = PageVisit.objects.filter(timestamp__date=now.date()).count()

    # Top Pages
    top_pages = (visits_qs.values('path')
    .annotate(count=Count('id'))
    .order_by('-count')[:5])

    # --- NEU: DATEN FÜR DIAGRAMM VORBEREITEN ---
    # Gruppieren nach Tag
    daily_data = (visits_qs
                  .annotate(date=TruncDate('timestamp'))
                  .values('date')
                  .annotate(count=Count('id'))
                  .order_by('date'))

    # Dictionary erstellen für schnellen Zugriff: { '2023-10-01': 50, ... }
    daily_dict = {item['date']: item['count'] for item in daily_data}

    chart_labels = []
    chart_data = []

    # Schleife über die letzten 30 Tage, um auch Nullen aufzufüllen
    for i in range(30):
        # Wir gehen vom ältesten Datum zum heutigen
        d = (now - timedelta(days=29 - i)).date()

        # Label formatieren (z.B. "30.11.")
        chart_labels.append(d.strftime("%d.%m."))

        # Daten holen (0 wenn kein Eintrag existiert)
        chart_data.append(daily_dict.get(d, 0))

    stats = {
        "total_visits": total_visits,
        "unique_visitors": unique_visitors,
        "today_visits": today_visits,
        "top_pages": top_pages,
        # Für das Diagramm:
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    }

    context = {
        # ... (restlicher Context bleibt gleich)
        "stats": stats,
    }
    return render(request, "admin_dashboard/dashboard_home.html", context)

@login_required
@require_POST
def dashboard_media_update(request):
    """
    Bild für einen bestimmten Slot (z.B. 'home_hero', 'home_about_image', 'logo')
    hochladen/aktualisieren.
    Nur Staff-User/Admins dürfen das.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden("Nicht erlaubt.")

    media_key = request.POST.get("media_key")
    image_file = request.FILES.get("image")
    alt_text = request.POST.get("alt_text", "").strip()

    if not media_key or not image_file:
        messages.error(request, "Bitte Slot und Bild auswählen.")
        return redirect("dashboard_home")

    # Hole oder erstelle den passenden SiteImage-Eintrag
    obj, _created = SiteImage.objects.get_or_create(key=media_key)
    obj.image = image_file
    obj.alt_text = alt_text
    obj.save()

    messages.success(request, f"Bild für Slot „{media_key}“ wurde aktualisiert.")
    return redirect("dashboard_home")

@login_required
def answer_catering_request(request, pk):
    """
    Antwortet auf eine Catering-Anfrage und verschickt eine E-Mail.
    """
    req = get_object_or_404(CateringRequest, pk=pk)

    if request.method == "POST":
        reply_text = request.POST.get("reply_text", "").strip()
        if reply_text:
            send_mail(
                subject="Ihre Catering-Anfrage bei KBG",
                message=reply_text,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[req.email],
            )
            req.status = CateringRequest.Status.ANSWERED
            req.reply_text = reply_text
            req.replied_at = timezone.now()
            req.save()
            messages.success(request, "Antwort wurde gesendet.")
        else:
            messages.error(request, "Antworttext darf nicht leer sein.")

    return redirect("dashboard_home")


@login_required
def answer_contact_request(request, pk):
    """
    Antwortet auf eine Kontakt-Anfrage und verschickt eine E-Mail.
    """
    req = get_object_or_404(ContactRequest, pk=pk)

    if request.method == "POST":
        reply_text = request.POST.get("reply_text", "").strip()
        if reply_text:
            send_mail(
                subject="Ihre Anfrage bei KBG",
                message=reply_text,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[req.email],
            )
            req.status = ContactRequest.Status.ANSWERED
            req.reply_text = reply_text
            req.replied_at = timezone.now()
            req.save()
            messages.success(request, "Antwort wurde gesendet.")
        else:
            messages.error(request, "Antworttext darf nicht leer sein.")

    return redirect("dashboard_home")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def dashboard_create_user(request):
    """
    Admin legt einen neuen Benutzer an.
    Passwort wird automatisch generiert und per Mail versendet.
    """
    if request.method != "POST":
        return redirect("dashboard_home")

    username = request.POST.get("new_username", "").strip()
    email = request.POST.get("new_email", "").strip()
    role = request.POST.get("new_role", "common")

    if not username or not email:
        messages.error(request, "Bitte Benutzername und E-Mail angeben.")
        return redirect("dashboard_home")

    if User.objects.filter(username=username).exists():
        messages.error(request, "Ein Benutzer mit diesem Benutzernamen existiert bereits.")
        return redirect("dashboard_home")

    if User.objects.filter(email=email).exists():
        messages.error(request, "Ein Benutzer mit dieser E-Mail existiert bereits.")
        return redirect("dashboard_home")

    # ein brauchbarer Zeichenvorrat ohne verwechselbare Zeichen wie 0/O, 1/l
    charset = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    password = get_random_string(12, allowed_chars=charset)

    is_admin = (role == "admin")

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=True,             # darf ins Backend / Dashboard
        is_superuser=is_admin,     # Admin oder Common User
    )

    # Profil-Flag setzen: muss Passwort ändern
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.must_change_password = True
    profile.save()

    # Login-URL bauen
    login_url = request.build_absolute_uri(reverse("login"))

    subject = "Zugang zum KBG Dashboard"
    message = (
        f"Hallo {username},\n\n"
        "du wurdest für das KBG-Dashboard freigeschaltet.\n\n"
        f"Login-URL: {login_url}\n"
        f"Benutzername: {username}\n"
        f"Passwort (bitte beim ersten Login ändern): {password}\n\n"
        "Beim ersten Login wirst du gebeten, dein eigenes Passwort zu setzen.\n\n"
        "Viele Grüße\n"
        "KBG Europe"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[email],
        fail_silently=True,  # im Test egal, geht in die Konsole
    )

    messages.success(request, "Benutzer wurde angelegt. E-Mail wurde gesendet (oder im Testsystem geloggt).")
    return redirect("dashboard_home")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def dashboard_delete_user(request, pk):
    """
    Admin kann Benutzer löschen.
    """
    if request.method != "POST":
        return redirect("dashboard_home")

    user_to_delete = get_object_or_404(User, pk=pk)

    if user_to_delete == request.user:
        messages.error(request, "Du kannst dich nicht selbst löschen.")
        return redirect("dashboard_home")

    user_to_delete.delete()
    messages.success(request, "Benutzer wurde gelöscht.")
    return redirect("dashboard_home")

@login_required
def force_password_change(request):
    """
    Seite, auf der Nutzer beim ersten Login ein neues Passwort setzen müssen.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Falls Flag schon weg ist, direkt ins Dashboard
    if not profile.must_change_password:
        return redirect("dashboard_home")

    if request.method == "POST":
        pw1 = request.POST.get("new_password1")
        pw2 = request.POST.get("new_password2")

        if not pw1 or not pw2:
            messages.error(request, "Bitte beide Passwort-Felder ausfüllen.")
        elif pw1 != pw2:
            messages.error(request, "Die Passwörter stimmen nicht überein.")
        else:
            # Passwort setzen
            user = request.user
            user.set_password(pw1)
            user.save()

            # Profil-Flag zurücksetzen
            profile.must_change_password = False
            profile.save()

            # Session behalten, obwohl Passwort geändert wurde
            update_session_auth_hash(request, user)

            messages.success(request, "Passwort wurde geändert.")
            return redirect("dashboard_home")

    return render(request, "admin_dashboard/force_password_change.html")


@login_required
def dashboard_home(request):
    # ... (Passwort Check bleibt) ...

    # 1. Anfragen laden (Sortierung: Neueste zuerst)
    catering_requests = CateringRequest.objects.order_by("-created_at")[:50]
    contact_requests = ContactRequest.objects.order_by("-created_at")[:50]
    users = User.objects.all().order_by("-is_superuser", "username")

    # 2. Bilder laden
    all_images = SiteImage.objects.all()
    site_images = {img.key: img for img in all_images}

    # 3. ECHTE STATISTIKEN BERECHNEN
    last_30_days = timezone.now() - timedelta(days=30)
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Alle Besuche der letzten 30 Tage
    visits_qs = PageVisit.objects.filter(timestamp__gte=last_30_days)

    total_visits = visits_qs.count()

    # Unique Visitors (basierend auf session_key)
    unique_visitors = visits_qs.values('session_key').distinct().count()

    # Besuche heute
    today_visits = PageVisit.objects.filter(timestamp__gte=today_start).count()

    # Top Seiten (Top 5)
    top_pages = (visits_qs
    .values('path')
    .annotate(count=Count('id'))
    .order_by('-count')[:5])

    stats = {
        "total_visits": total_visits,
        "unique_visitors": unique_visitors,
        "today_visits": today_visits,
        "top_pages": top_pages,
    }

    context = {
        "catering_requests": catering_requests,
        "contact_requests": contact_requests,
        "users": users,
        "site_images": site_images,
        "stats": stats,  # NEU: Stats übergeben
    }
    return render(request, "admin_dashboard/dashboard_home.html", context)
