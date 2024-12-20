from django.db import models


class Shop(models.Model):
    """Model for storing shop information"""
    name = models.CharField(max_length=255)
    address = models.TextField()
    manager_name = models.CharField(max_length=255)
    manager_phone = models.CharField(max_length=20)
    manager_email = models.EmailField()
    store_manager_name = models.CharField(max_length=255)
    store_manager_phone = models.CharField(max_length=20)
    store_manager_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MainStore(models.Model):
    """Model for storing main store information"""
    name = models.CharField(max_length=255)
    address = models.TextField()
    manager_name = models.CharField(max_length=255)
    manager_phone = models.CharField(max_length=20)
    manager_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

