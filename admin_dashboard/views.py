from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from pages.models import CateringRequest, ContactRequest, SiteImage
from django.views.decorators.http import require_POST



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
            return redirect("dashboard_home")
        else:
            messages.error(request, "Benutzername oder Passwort ist falsch.")

    return render(request, "admin_dashboard/login.html")


@login_required
def dashboard_home(request):
    catering_requests = CateringRequest.objects.order_by("-created_at")[:50]
    contact_requests = ContactRequest.objects.order_by("-created_at")[:50]
    site_images = {img.key: img for img in SiteImage.objects.all()}

    context = {
        "catering_requests": catering_requests,
        "contact_requests": contact_requests,
        "site_images": site_images,
    }
    return render(request, "admin_dashboard/dashboard_home.html", context)


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
@require_POST
def update_site_image(request):
    """
    Verarbeitet Uploads aus dem Medien-Tab.
    """
    key = request.POST.get("media_key")
    img_file = request.FILES.get("image")
    alt_text = request.POST.get("alt_text", "").strip()

    if not key or not img_file:
        messages.error(request, "Bitte einen Bild-Slot und eine Datei auswählen.")
        return redirect("dashboard_home")

    obj, created = SiteImage.objects.get_or_create(key=key)

    # altes Bild löschen (Datei), wenn vorhanden
    if obj.image and obj.image.name and obj.image.storage.exists(obj.image.name):
        obj.image.delete(save=False)

    obj.image = img_file
    if alt_text:
        obj.alt_text = alt_text
    obj.save()

    messages.success(request, f"Bild für '{key}' wurde aktualisiert.")
    return redirect("dashboard_home")
