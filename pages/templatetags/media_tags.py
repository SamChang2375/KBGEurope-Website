from django import template
from django.templatetags.static import static
from pages.models import SiteImage

register = template.Library()


@register.simple_tag
def site_image_url(key, default_static_path):
    """
    Liefert die URL des SiteImage mit dem gegebenen key.
    Wenn keins existiert, wird der static()-Pfad verwendet.
    """
    try:
        obj = SiteImage.objects.get(key=key)
        if obj.image:
            return obj.image.url
    except SiteImage.DoesNotExist:
        pass
    return static(default_static_path)


@register.simple_tag
def site_image_alt(key, default_alt=""):
    """
    Liefert den Alt-Text des SiteImage; sonst Default-Wert.
    """
    try:
        obj = SiteImage.objects.get(key=key)
        if obj.alt_text:
            return obj.alt_text
    except SiteImage.DoesNotExist:
        pass
    return default_alt
