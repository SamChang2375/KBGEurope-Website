from .models import SiteImage

def global_social_data(request):
    """
    Macht Social-Media-Icons und Links auf allen Seiten verfügbar.
    Wird in base.html als {{ global_social_icons }} genutzt.
    """
    # Bilder aus der Datenbank holen
    insta_img_obj = SiteImage.objects.filter(key="instagram_icon").first()
    email_img_obj = SiteImage.objects.filter(key="email_icon").first()

    return {
        "global_social_icons": {
            # Wir übergeben das Image-Field-Objekt, damit .url im Template funktioniert
            "instagram_icon": insta_img_obj.image if (insta_img_obj and insta_img_obj.image) else None,
            "email_icon": email_img_obj.image if (email_img_obj and email_img_obj.image) else None,

            # Links (Da dein Model keine Link-Felder hat, definieren wir sie hier oder hardcoded)
            "instagram_url": "https://www.instagram.com/kbg_europe/",
            "email": "info@kbg-europe.de",
        }
    }