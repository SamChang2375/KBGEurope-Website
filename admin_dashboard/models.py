from django.db import models
from django.contrib.auth.models import User

class ContactRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    answered = models.BooleanField(default=False)
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anfrage von {self.name}"

class CateringRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    answered = models.BooleanField(default=False)
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Catering Anfrage von {self.name}"

class Media(models.Model):
    image = models.ImageField(upload_to='media/images/')
    title = models.CharField(max_length=255)
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class SEO(models.Model):
    title = models.CharField(max_length=255)
    meta_description = models.TextField()
    keywords = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return f"Profil für {self.user.username}"

class PageVisit(models.Model):
    path = models.CharField(max_length=255)  # z.B. "/" oder "/menu"
    timestamp = models.DateTimeField(auto_now_add=True)
    # Optional: Session Key für Unique Visitors (einfach gehalten)
    session_key = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.path} at {self.timestamp}"