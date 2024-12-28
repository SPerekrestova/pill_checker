from django.db import models
from django.contrib.auth.models import AbstractUser

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.image.name


# Custom user model
class CustomUser(AbstractUser):
    # Additional fields for user details
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    supabase_user_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


# Model to store scanned medications
class ScannedMedication(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='scanned_medications')
    medication_name = models.CharField(max_length=255)
    scan_date = models.DateTimeField(auto_now_add=True)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    prescription_details = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.medication_name} - {self.user.username}"
