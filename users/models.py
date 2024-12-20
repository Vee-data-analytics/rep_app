from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    ADMIN = 'admin'
    REPRESENTATIVE = 'representative'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (REPRESENTATIVE, 'Field Representative'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=REPRESENTATIVE
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name="Phone Number"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active."
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
        help_text='Specific permissions for this user.'
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name if full_name else self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        # Ensure admin users have proper permissions
        if self.role == self.ADMIN:
            self.is_staff = True
            if not self.is_superuser and self.username == 'admin':
                self.is_superuser = True
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_representative(self):
        return self.role == self.REPRESENTATIVE

    def clean(self):
        super().clean()
        if self.is_superuser and self.role != self.ADMIN:
            raise ValidationError('Superusers must have admin role.')