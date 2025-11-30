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


class SiteSettings(models.Model):
    # Allgemeine Einstellungen
    address = models.CharField(max_length=255, default="Poststraße 2–4, 53111 Bonn")
    opening_hours = models.CharField(max_length=255, default="Montag bis Samstag, 11:00–20:30 Uhr")
    phone = models.CharField(max_length=100, default="+49 228 88690432")
    email = models.EmailField(default="info@kbg-europe.de")

    # Bestell Buttons
    btn_pickup_text = models.CharField(max_length=50, default="Abholen")
    btn_pickup_link = models.CharField(max_length=255, default="#", blank=True)
    btn_wolt_text = models.CharField(max_length=50, default="Wolt")
    btn_wolt_link = models.CharField(max_length=255, default="https://wolt.com", blank=True)
    btn_lieferando_text = models.CharField(max_length=50, default="Lieferando")
    btn_lieferando_link = models.CharField(max_length=255, default="https://lieferando.de", blank=True)
    btn_uber_text = models.CharField(max_length=50, default="Uber Eats")
    btn_uber_link = models.CharField(max_length=255, default="https://ubereats.com", blank=True)

    def __str__(self):
        return "Globale Seiteneinstellungen"


class MenuItem(models.Model):
    """
    Repräsentiert einen einzelnen Menü-Block.
    """
    order = models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")
    dish_id = models.CharField(max_length=10, blank=True, verbose_name="Nummer")
    name = models.CharField(max_length=200, verbose_name="Gericht Name")
    subtitle = models.CharField(max_length=255, blank=True, verbose_name="Untertitel")
    description_de = models.TextField(blank=True, verbose_name="Beschreibung DE")
    description_en = models.TextField(blank=True, verbose_name="Beschreibung EN")
    options_text = models.TextField(blank=True, verbose_name="Optionen", help_text="Eine Option pro Zeile.")
    image = models.ImageField(upload_to="menu_items/", verbose_name="Gericht Bild")
    background_image = models.ImageField(upload_to="menu_bg/", blank=True, null=True, verbose_name="Hintergrundbild")
    background_color = models.CharField(max_length=50, blank=True, default="#ffffff",
                                        verbose_name="Hintergrundfarbe (Hex)")

    def get_options_list(self):
        if not self.options_text:
            return []
        lines = self.options_text.strip().split('\n')
        result = []
        for line in lines:
            line = line.strip()
            parts = line.split(' ', 1)
            if len(parts) == 2:
                result.append({'code': parts[0], 'label': parts[1]})
            else:
                result.append({'code': '', 'label': line})
        return result

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.dish_id} {self.name}"


# --- NEU HINZUFÜGEN: JOB MODELLE ---

class JobOffer(models.Model):
    """
    Repräsentiert ein dynamisches Stellenangebot (Liste), falls benötigt.
    """
    order = models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")
    title = models.CharField(max_length=200, verbose_name="Job Titel", default="Mitarbeiter (m/w/d)")
    description = models.TextField(verbose_name="Beschreibung / Punkte",
                                   help_text="Jede neue Zeile wird ein Stichpunkt.")
    image = models.ImageField(upload_to="jobs/", verbose_name="Vorschaubild", blank=True, null=True)
    button_link = models.CharField(max_length=255, default="mailto:jobs@kbg-europe.de",
                                   verbose_name="Link für Bewerbung")
    button_text = models.CharField(max_length=50, default="Zur Bewerbung", verbose_name="Button Text")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_points(self):
        return [x.strip() for x in self.description.split('\n') if x.strip()]


class JobContent(models.Model):
    """
    Inhalte für die 3 statischen Job-Karten (Shopleiter, Service, Koch).
    """
    JOB_TYPES = [
        ('manager', 'Shopleiter (m/w/d)'),
        ('service', 'Service (m/w/d)'),
        ('cook', 'Koch (m/w/d)'),
    ]

    job_type = models.CharField(max_length=20, choices=JOB_TYPES, unique=True)
    image = models.ImageField(upload_to="jobs/content/", verbose_name="Vorschaubild", blank=True, null=True)
    short_description = models.TextField(verbose_name="Listenpunkte auf Karte", help_text="Jede Zeile ein Punkt.",
                                         blank=True)
    popup_title = models.CharField(max_length=200, verbose_name="Popup Titel",
                                   default="(Studentische) Aushilfskraft (m/w)")
    popup_text = models.TextField(verbose_name="Popup Text (Anforderungen)", help_text="Der Text im Popup links.",
                                  blank=True)

    def get_points(self):
        if not self.short_description:
            return []
        return [x.strip() for x in self.short_description.split('\n') if x.strip()]

    def __str__(self):
        return self.get_job_type_display()


class JobApplication(models.Model):
    """
    Eingehende Bewerbung.
    """
    STATUS_CHOICES = [
        ('new', 'Neu / Unbearbeitet'),
        ('processed', 'Bearbeitet'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    job_type = models.CharField(max_length=50, verbose_name="Bewerbung für")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    cover_letter = models.FileField(upload_to="applications/cover_letters/", verbose_name="Anschreiben")
    cv = models.FileField(upload_to="applications/cvs/", verbose_name="Lebenslauf")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.job_type})"