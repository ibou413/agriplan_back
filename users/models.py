# userapp/models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    professional_activity = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    
    ACCOUNT_TYPE_CHOICES = [
        ('producer', 'Producteur'),
        ('seller', 'Vendeur'),
    ]
    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPE_CHOICES,
        default='producer'
    )

    # Groupes et permissions
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Nom personnalisé pour éviter les conflits
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",  # Nom personnalisé pour éviter les conflits
        blank=True
    )

    def __str__(self):
        return self.username
