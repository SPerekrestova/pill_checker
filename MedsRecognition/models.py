from django.db import models
from django.contrib.auth.models import AbstractUser

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name


class CustomUser(AbstractUser):
    supabase_user_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.username