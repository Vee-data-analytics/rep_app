from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('REP', 'Store Representative'),
        ('STORE_ADMIN', 'Store Administrator'),
        ('WAREHOUSE_ADMIN', 'Warehouse Administrator'),
        ('STORAGE_ADMIN', 'Storage Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True)
    assigned_location = models.ForeignKey('site_shop.Location', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    ADMIN = 'admin'
    REPRESENTATIVE = 'representative'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (REPRESENTATIVE, 'Field Representative'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=REPRESENTATIVE)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
