from django.conf import settings
from django.db import models


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField(blank=True, null=True)

    def __str__(self):
        # Use a fallback to avoid AttributeError on missing image or name
        return self.image.name if self.image and hasattr(self.image, 'name') else "No Image"


class ScannedMedication(models.Model):
    # Replace the custom User class with Django's AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scanned_medications'
    )
    medication_name = models.CharField(max_length=255)
    scan_date = models.DateTimeField(auto_now_add=True)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    prescription_details = models.JSONField(blank=True, null=True)

    def __str__(self):
        # Use getattr to safely access the user's username
        username = getattr(self.user, 'username', 'Unknown User')
        return f"{self.medication_name} - {username}"

