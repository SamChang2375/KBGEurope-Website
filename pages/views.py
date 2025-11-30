from django.shortcuts import render, redirect
from .models import CateringRequest, ContactRequest, JobOffer
from django.contrib import messages
from .models import MenuItem, CateringRequest, ContactRequest, SiteImage, SiteSettings # MenuItem importieren

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
    jobs = JobOffer.objects.all().order_by('order')
    return render(request, "pages/jobs.html", {"jobs": jobs})

