from .models import SiteImage, SiteSettings  # SiteSettings importieren!

def global_social_data(request):
    # Bilder holen (wie bisher)
    insta_img_obj = SiteImage.objects.filter(key="instagram_icon").first()
    email_img_obj = SiteImage.objects.filter(key="email_icon").first()

    # --- NEU: Einstellungen holen ---
    # Wir holen das erste Objekt oder erstellen eins mit Default-Werten, falls keins da ist
    settings_obj, created = SiteSettings.objects.get_or_create(id=1)

    return {
        "global_social_icons": {
            "instagram_icon": insta_img_obj.image if (insta_img_obj and insta_img_obj.image) else None,
            "email_icon": email_img_obj.image if (email_img_obj and email_img_obj.image) else None,
            # Links greifen jetzt auf das Settings-Objekt zu
            "instagram_url": "https://www.instagram.com/kbg_europe/",
            "email": settings_obj.email,
        },
        # Das gesamte Settings-Objekt verfügbar machen
        "site_settings": settings_obj,
    }