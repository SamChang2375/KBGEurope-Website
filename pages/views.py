from django.shortcuts import render, redirect
from .models import CateringRequest, ContactRequest, JobContent, JobApplication
from django.contrib import messages
from .models import MenuItem, CateringRequest, ContactRequest, SiteImage, SiteSettings # MenuItem importieren
from django.core.mail import send_mail
from django.conf import settings
from .models import JobContent, JobApplication

def home_view(request):
    return render(request, "pages/home.html")

def menu_view(request):
    menu_items = MenuItem.objects.all().order_by('order')
    return render(request, "pages/menu.html", {"menu_items": menu_items})

def bestellen_view(request):
    return render(request, "pages/bestellen.html")

def catering_view(request):
    if request.method == "POST":
        CateringRequest.objects.create(
            contact_person=request.POST.get("contact_person", "").strip(),
            company=request.POST.get("company", "").strip(),
            email=request.POST.get("email", "").strip(),
            phone=request.POST.get("phone", "").strip(),
            address=request.POST.get("address", "").strip(),
            message=request.POST.get("message", "").strip(),
            agreed_privacy=bool(request.POST.get("privacy")),
        )
        messages.success(request, "Vielen Dank! Ihre Catering-Anfrage wurde gesendet.")
        return redirect("catering")  # reload mit Erfolgsmeldung

    return render(request, "pages/catering.html")

def kontakt_view(request):
    if request.method == "POST":
        ContactRequest.objects.create(
            name=request.POST.get("name", "").strip(),
            email=request.POST.get("email", "").strip(),
            message=request.POST.get("message", "").strip(),
        )
        messages.success(request, "Vielen Dank! Ihre Nachricht wurde gesendet.")
        return redirect("kontakt")

    return render(request, "pages/kontakt.html")


def jobs_view(request):
    # Inhalte laden (oder Default-Objekte erstellen, falls leer)
    # Wir stellen sicher, dass für jeden Typ ein Objekt existiert
    job_types = ['manager', 'service', 'cook']
    jobs = {}
    for jt in job_types:
        obj, created = JobContent.objects.get_or_create(job_type=jt)
        jobs[jt] = obj

    if request.method == "POST":
        # Bewerbung speichern
        application = JobApplication.objects.create(
            job_type=request.POST.get('job_type_label', 'Allgemein'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            cover_letter=request.FILES.get('cover_letter'),
            cv=request.FILES.get('cv')
        )

        # E-Mail an Peter senden
        subject = f"Neue Bewerbung: {application.first_name} {application.last_name}"
        message = (
            f"Es ist eine neue Bewerbung für '{application.job_type}' eingegangen.\n\n"
            f"Name: {application.first_name} {application.last_name}\n"
            f"Email: {application.email}\n\n"
            "Bitte prüfe das Dashboard für Details und Anhänge."
        )

        # fail_silently=True damit der User keinen Fehler sieht, falls Mailserver spinnt
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['peter.ryu@kbg-europe.de'], fail_silently=True)

        # Success Flag für Template (zeigt Popup und Redirect)
        return render(request, "pages/jobs.html", {"jobs": jobs, "success": True})

    return render(request, "pages/jobs.html", {"jobs": jobs})