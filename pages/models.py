from django.db import models

class CateringRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Offen"
        ANSWERED = "answered", "Beantwortet"

    created_at = models.DateTimeField(auto_now_add=True)

    contact_person = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    agreed_privacy = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    reply_text = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Catering-Anfrage von {self.contact_person} ({self.created_at:%d.%m.%Y})"


class ContactRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Offen"
        ANSWERED = "answered", "Beantwortet"

    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    reply_text = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Kontakt-Anfrage von {self.name} ({self.created_at:%d.%m.%Y})"

class SiteImage(models.Model):
    """
    Ein Bild-Slot auf der Website, z.B. 'home_hero', 'menu_hero', 'global_logo' etc.
    Jeder key ist eindeutig.
    """
    key = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="site_images/")
    alt_text = models.CharField(max_length=255, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key