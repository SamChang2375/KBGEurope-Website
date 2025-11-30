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
    # ... (deine bestehenden Felder: address, opening_hours, phone, email) ...
    address = models.CharField(max_length=255, default="Poststraße 2–4, 53111 Bonn")
    opening_hours = models.CharField(max_length=255, default="Montag bis Samstag, 11:00–20:30 Uhr")
    phone = models.CharField(max_length=100, default="+49 228 88690432")
    email = models.EmailField(default="info@kbg-europe.de")

    # --- NEU: BESTELLEN BUTTONS ---
    # Button 1: Abholen
    btn_pickup_text = models.CharField(max_length=50, default="Abholen")
    btn_pickup_link = models.CharField(max_length=255, default="#", blank=True)

    # Button 2: Wolt
    btn_wolt_text = models.CharField(max_length=50, default="Wolt")
    btn_wolt_link = models.CharField(max_length=255, default="https://wolt.com", blank=True)

    # Button 3: Lieferando
    btn_lieferando_text = models.CharField(max_length=50, default="Lieferando")
    btn_lieferando_link = models.CharField(max_length=255, default="https://lieferando.de", blank=True)

    # Button 4: Uber Eats
    btn_uber_text = models.CharField(max_length=50, default="Uber Eats")
    btn_uber_link = models.CharField(max_length=255, default="https://ubereats.com", blank=True)

    def __str__(self):
        return "Globale Seiteneinstellungen"

class MenuItem(models.Model):
    """
    Repräsentiert einen einzelnen Menü-Block (z.B. "1 Bibimbap").
    """
    order = models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")

    # Inhalte
    dish_id = models.CharField(max_length=10, blank=True, verbose_name="Nummer", help_text="z.B. '1' oder '11'")
    name = models.CharField(max_length=200, verbose_name="Gericht Name")
    subtitle = models.CharField(max_length=255, blank=True, verbose_name="Untertitel")

    description_de = models.TextField(blank=True, verbose_name="Beschreibung DE")
    description_en = models.TextField(blank=True, verbose_name="Beschreibung EN")

    # Optionen: Wir speichern das als Text. Jede Zeile eine Option.
    # z.B.: "1A Bulgogi Beef"
    options_text = models.TextField(blank=True, verbose_name="Optionen",
                                    help_text="Eine Option pro Zeile. Der Code (z.B. 1A) wird automatisch erkannt.")

    # Bilder & Design
    image = models.ImageField(upload_to="menu_items/", verbose_name="Gericht Bild")
    background_image = models.ImageField(upload_to="menu_bg/", blank=True, null=True, verbose_name="Hintergrundbild")
    background_color = models.CharField(max_length=50, blank=True, default="#ffffff",
                                        verbose_name="Hintergrundfarbe (Hex)")

    def get_options_list(self):
        """Hilfsfunktion: Wandelt den Textblock in eine Liste um."""
        if not self.options_text:
            return []
        lines = self.options_text.strip().split('\n')
        result = []
        for line in lines:
            line = line.strip()
            # Versuch, den Code am Anfang zu trennen (erstes Leerzeichen)
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


class JobOffer(models.Model):
    """
    Repräsentiert ein Stellenangebot auf der Karriere-Seite.
    """
    order = models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")
    title = models.CharField(max_length=200, verbose_name="Job Titel", default="Mitarbeiter (m/w/d)")

    # Wir speichern die Aufzählungspunkte als Text. Jede neue Zeile = ein Punkt.
    description = models.TextField(verbose_name="Beschreibung / Punkte",
                                   help_text="Jede neue Zeile wird ein Stichpunkt.")

    image = models.ImageField(upload_to="jobs/", verbose_name="Vorschaubild")

    # Optional, falls jeder Job woanders hinführt (z.B. Mailto oder Formular)
    button_link = models.CharField(max_length=255, default="mailto:jobs@kbg-europe.de",
                                   verbose_name="Link für Bewerbung")
    button_text = models.CharField(max_length=50, default="Zur Bewerbung", verbose_name="Button Text")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_points(self):
        """Hilfsfunktion: Wandelt Text in Liste für Template um"""
        return [x.strip() for x in self.description.split('\n') if x.strip()]