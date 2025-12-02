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
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

# Modelle importieren
from pages.models import (
    CateringRequest,
    ContactRequest,
    SiteImage,
    SiteSettings,
    MenuItem,
    JobOffer,
    JobContent,
    JobApplication
)
from .models import UserProfile, PageVisit

User = get_user_model()


# --- LOGIN VIEW ---
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if profile.must_change_password:
                return redirect("force_password_change")
            return redirect("dashboard_home")
        else:
            messages.error(request, "Benutzername oder Passwort ist falsch.")
    return render(request, "admin_dashboard/login.html")


# --- DASHBOARD HOME (ALLE DATEN LADEN) ---
@login_required
def dashboard_home(request):
    # 1. Passwort-Check
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.must_change_password:
        return redirect("force_password_change")

    # 2. Daten laden (Anfragen & User)
    catering_requests = CateringRequest.objects.order_by("-created_at")[:50]
    contact_requests = ContactRequest.objects.order_by("-created_at")[:50]
    users = User.objects.all().order_by("-is_superuser", "username")

    # 3. Bilder laden
    all_images = SiteImage.objects.all()
    site_images = {img.key: img for img in all_images}

    # 4. Settings laden
    site_settings, _ = SiteSettings.objects.get_or_create(id=1)

    # 5. STATISTIKEN BERECHNEN
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    visits_qs = PageVisit.objects.filter(timestamp__gte=last_30_days)

    total_visits = visits_qs.count()
    unique_visitors = visits_qs.values('session_key').distinct().count()
    today_visits = PageVisit.objects.filter(timestamp__gte=today_start).count()

    top_pages = (visits_qs.values('path')
    .annotate(count=Count('id'))
    .order_by('-count')[:5])

    # Diagramm-Daten
    daily_data = (visits_qs
                  .annotate(date=TruncDate('timestamp'))
                  .values('date')
                  .annotate(count=Count('id'))
                  .order_by('date'))

    daily_dict = {item['date']: item['count'] for item in daily_data}
    chart_labels = []
    chart_data = []

    for i in range(30):
        d = (now - timedelta(days=29 - i)).date()
        chart_labels.append(d.strftime("%d.%m."))
        chart_data.append(daily_dict.get(d, 0))

    stats = {
        "total_visits": total_visits,
        "unique_visitors": unique_visitors,
        "today_visits": today_visits,
        "top_pages": top_pages,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    }

    # 6. MENÜ ITEMS LADEN
    menu_items = MenuItem.objects.all().order_by('dish_id')

    # 7. JOBS LADEN
    # a) Die dynamische Liste
    jobs = JobOffer.objects.all().order_by('order')

    # b) Die 3 statischen Job-Karten Inhalte
    job_contents = {}
    for jt in ['manager', 'service', 'cook']:
        job_contents[jt], _ = JobContent.objects.get_or_create(job_type=jt)

    # c) Bewerbungen laden (neueste zuerst)
    applications = JobApplication.objects.all().order_by('-created_at')

    # Context zusammenbauen
    context = {
        "catering_requests": catering_requests,
        "contact_requests": contact_requests,
        "users": users,
        "site_images": site_images,
        "site_settings": site_settings,
        "stats": stats,
        "menu_items": menu_items,
        "jobs": jobs,  # Für die Liste der Stellenanzeigen
        "job_contents": job_contents,  # Für die 3 Karten (Bild/Text/Popup)
        "applications": applications,  # Für die Tabelle
    }
    return render(request, "admin_dashboard/dashboard_home.html", context)


# --- MEDIA UPDATE ---
@login_required
@require_POST
def dashboard_media_update(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Nicht erlaubt.")

    media_key = request.POST.get("media_key")
    image_file = request.FILES.get("image")
    alt_text = request.POST.get("alt_text", "").strip()

    if not media_key:
        messages.error(request, "Fehler: Kein Media-Key.")
        return redirect("dashboard_home")

    obj, created = SiteImage.objects.get_or_create(key=media_key)

    if image_file:
        obj.image = image_file

    obj.alt_text = alt_text
    obj.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "admin_dashboard/dashboard_home.html", {})

    messages.success(request, f"Gespeichert: {media_key}")
    return redirect("dashboard_home")


# --- SETTINGS UPDATE ---
@login_required
@require_POST
def dashboard_settings_update(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    settings_obj, _ = SiteSettings.objects.get_or_create(id=1)

    # Felder speichern (verwende get um Fehler zu vermeiden, falls Feld nicht im Formular)
    settings_obj.address = request.POST.get("address", settings_obj.address)
    settings_obj.opening_hours = request.POST.get("opening_hours", settings_obj.opening_hours)
    settings_obj.phone = request.POST.get("phone", settings_obj.phone)
    settings_obj.email = request.POST.get("email", settings_obj.email)

    settings_obj.btn_pickup_text = request.POST.get("btn_pickup_text", settings_obj.btn_pickup_text)
    settings_obj.btn_pickup_link = request.POST.get("btn_pickup_link", settings_obj.btn_pickup_link)
    settings_obj.btn_wolt_text = request.POST.get("btn_wolt_text", settings_obj.btn_wolt_text)
    settings_obj.btn_wolt_link = request.POST.get("btn_wolt_link", settings_obj.btn_wolt_link)
    settings_obj.btn_lieferando_text = request.POST.get("btn_lieferando_text", settings_obj.btn_lieferando_text)
    settings_obj.btn_lieferando_link = request.POST.get("btn_lieferando_link", settings_obj.btn_lieferando_link)
    settings_obj.btn_uber_text = request.POST.get("btn_uber_text", settings_obj.btn_uber_text)
    settings_obj.btn_uber_link = request.POST.get("btn_uber_link", settings_obj.btn_uber_link)

    settings_obj.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "admin_dashboard/dashboard_home.html", {})

    messages.success(request, "Einstellungen gespeichert.")
    return redirect("dashboard_home")


# --- ANFRAGEN BEANTWORTEN ---
@login_required
def answer_catering_request(request, pk):
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
            messages.success(request, "Antwort gesendet.")
    return redirect("dashboard_home")


@login_required
def answer_contact_request(request, pk):
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
            messages.success(request, "Antwort gesendet.")
    return redirect("dashboard_home")


# --- USER MANAGEMENT ---
@login_required
@user_passes_test(lambda u: u.is_superuser)
def dashboard_create_user(request):
    if request.method == "POST":
        username = request.POST.get("new_username", "").strip()
        email = request.POST.get("new_email", "").strip()
        role = request.POST.get("new_role", "common")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username existiert bereits.")
            return redirect("dashboard_home")

        password = get_random_string(12)
        is_admin = (role == "admin")

        user = User.objects.create_user(username=username, email=email, password=password, is_staff=True,
                                        is_superuser=is_admin)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.must_change_password = True
        profile.save()

        messages.success(request, "Benutzer angelegt.")
    return redirect("dashboard_home")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def dashboard_delete_user(request, pk):
    if request.method == "POST":
        u = get_object_or_404(User, pk=pk)
        if u != request.user:
            u.delete()
            messages.success(request, "Gelöscht.")
    return redirect("dashboard_home")


@login_required
def force_password_change(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.must_change_password:
        return redirect("dashboard_home")

    if request.method == "POST":
        pw1 = request.POST.get("new_password1")
        pw2 = request.POST.get("new_password2")
        if pw1 == pw2:
            request.user.set_password(pw1)
            request.user.save()
            profile.must_change_password = False
            profile.save()
            update_session_auth_hash(request, request.user)
            return redirect("dashboard_home")
        else:
            messages.error(request, "Passwörter stimmen nicht überein.")

    return render(request, "admin_dashboard/force_password_change.html")


# --- MENU ITEM MANAGEMENT ---

@login_required
@require_POST
def dashboard_menu_item_create(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    last_item = MenuItem.objects.last()
    new_order = (last_item.order + 1) if last_item else 1

    MenuItem.objects.create(
        order=new_order,
        dish_id=request.POST.get("dish_id", ""),
        name=request.POST.get("name", "Neues Gericht"),
        subtitle=request.POST.get("subtitle", ""),
        description_de=request.POST.get("description_de", ""),
        description_en=request.POST.get("description_en", ""),
        options_text=request.POST.get("options_text", ""),
        background_color=request.POST.get("background_color", "#ffffff"),
        image=request.FILES.get("image")
    )
    messages.success(request, "Menü-Block erstellt.")
    return redirect("dashboard_home")


@login_required
@require_POST
def dashboard_menu_item_update(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    item = get_object_or_404(MenuItem, pk=pk)
    item.dish_id = request.POST.get("dish_id", item.dish_id)
    item.name = request.POST.get("name", item.name)
    item.subtitle = request.POST.get("subtitle", item.subtitle)
    item.description_de = request.POST.get("description_de", item.description_de)
    item.description_en = request.POST.get("description_en", item.description_en)
    item.options_text = request.POST.get("options_text", item.options_text)
    item.background_color = request.POST.get("background_color", item.background_color)
    item.order = request.POST.get("order", item.order)

    if request.FILES.get("image"):
        item.image = request.FILES.get("image")
    if request.FILES.get("background_image"):
        item.background_image = request.FILES.get("background_image")
    if request.POST.get("delete_bg_image"):
        item.background_image = None

    item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "admin_dashboard/dashboard_home.html", {})

    messages.success(request, f"Menü '{item.name}' gespeichert.")
    return redirect("dashboard_home")


@login_required
@require_POST
def dashboard_menu_item_delete(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    item = get_object_or_404(MenuItem, pk=pk)
    item.delete()
    messages.success(request, "Menü-Block gelöscht.")
    return redirect("dashboard_home")


# --- JOB OFFER MANAGEMENT (Dynamische Liste) ---

@login_required
@require_POST
def dashboard_job_create(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    last_job = JobOffer.objects.last()
    new_order = (last_job.order + 1) if last_job else 1

    JobOffer.objects.create(
        order=new_order,
        title=request.POST.get("title", "Neuer Job"),
        description=request.POST.get("description", ""),
        button_link=request.POST.get("button_link", "mailto:jobs@kbg-europe.de"),
        image=request.FILES.get("image")
    )
    messages.success(request, "Job-Angebot erstellt.")
    return redirect("dashboard_home")


@login_required
@require_POST
def dashboard_job_update(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    job = get_object_or_404(JobOffer, pk=pk)
    job.title = request.POST.get("title", job.title)
    job.description = request.POST.get("description", job.description)
    job.button_link = request.POST.get("button_link", job.button_link)
    job.order = request.POST.get("order", job.order)

    if request.FILES.get("image"):
        job.image = request.FILES.get("image")

    job.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "admin_dashboard/dashboard_home.html", {})

    messages.success(request, f"Job '{job.title}' gespeichert.")
    return redirect("dashboard_home")


@login_required
@require_POST
def dashboard_job_delete(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    job = get_object_or_404(JobOffer, pk=pk)
    job.delete()
    messages.success(request, "Job gelöscht.")
    return redirect("dashboard_home")


# --- JOB CONTENT & BEWERBUNG (Die fehlenden Funktionen!) ---

@login_required
@require_POST
def dashboard_job_content_update(request):
    """Speichert Bilder und Texte der 3 statischen Job-Karten (Manager, Service, Koch)"""
    if not request.user.is_staff:
        return HttpResponseForbidden()

    # Wir loopen durch die 3 Typen und speichern die Eingaben
    for jt in ['manager', 'service', 'cook']:
        obj, _ = JobContent.objects.get_or_create(job_type=jt)

        # Beschreibung (Punkte auf Karte)
        short_desc = request.POST.get(f"{jt}_short_desc")
        if short_desc is not None:
            obj.short_description = short_desc

        # Popup Infos
        popup_title = request.POST.get(f"{jt}_popup_title")
        if popup_title is not None:
            obj.popup_title = popup_title

        popup_text = request.POST.get(f"{jt}_popup_text")
        if popup_text is not None:
            obj.popup_text = popup_text

        # Bild Update
        if request.FILES.get(f"{jt}_image"):
            obj.image = request.FILES.get(f"{jt}_image")

        obj.save()

    messages.success(request, "Job-Inhalte gespeichert.")
    return redirect("dashboard_home")


@login_required
def dashboard_application_processed(request, pk):
    """Setzt Status einer Bewerbung auf 'Bearbeitet'"""
    if not request.user.is_staff:
        return HttpResponseForbidden()

    app = get_object_or_404(JobApplication, pk=pk)
    app.status = 'processed'
    app.save()

    # Bei AJAX Requests einfach 200 OK zurückgeben, sonst Redirect
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "admin_dashboard/dashboard_home.html", {})

    return redirect("dashboard_home")