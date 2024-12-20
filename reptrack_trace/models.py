from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from users.models import User 

class Shop(models.Model):
    """Model for storing shop information"""
    name = models.CharField(max_length=255,null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    manager_name = models.CharField(max_length=255,null=True, blank=True)
    manager_phone = models.CharField(max_length=20,null=True, blank=True)
    manager_email = models.EmailField()
    store_manager_name = models.CharField(max_length=255,null=True, blank=True)
    store_manager_phone = models.CharField(max_length=20,null=True, blank=True)
    store_manager_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Store(models.Model):
    """Model to represent a Store"""
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    manager_name = models.CharField(max_length=255)
    manager_phone = models.CharField(max_length=20)
    manager_email = models.EmailField()
    store_manager_name = models.CharField(max_length=255, null=True, blank=True)
    store_manager_phone = models.CharField(max_length=20,null=True, blank=True)
    store_manager_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ShopStore(models.Model):
    """Model to represent the relationship between a Shop and a Store"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_stores')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_shops')
    quantity_taken= models.IntegerField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)  
    class Meta:
        unique_together = ('shop', 'store')  
    def __str__(self):
        return f"{self.shop.name} - {self.store.name}"

class MainStore(models.Model):
    """Model for storing main store information"""
    name = models.CharField(max_length=255)
    address = models.TextField()
    manager_name = models.CharField(max_length=255,null=True, blank=True)
    manager_phone = models.CharField(max_length=20,null=True, blank=True)
    manager_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Model for storing product information"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Report(models.Model):
    """Model for storing representative reports"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    representative = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Shop Section
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shop_current_quantity = models.IntegerField()
    needs_topup = models.BooleanField()
    desired_quantity = models.IntegerField(null=True, blank=True)
    topup_quantity = models.IntegerField(null=True, blank=True)
    shop_photo = models.ImageField(upload_to='shop_photos/')
    shop_comments = models.TextField(blank=True)
    
    # Shop-Stores Section
    shop_store_manager_confirmed = models.BooleanField(default=False)
    shop_store_current_quantity = models.IntegerField(null=True, blank=True)
    shop_store_has_sufficient_stock = models.BooleanField(null=True)
    quantity_taken_from_shop_store = models.IntegerField(null=True, blank=True)
    remaining_shop_store_quantity = models.IntegerField(null=True, blank=True)
    shop_store_photo = models.ImageField(upload_to='shop_store_photos/', null=True, blank=True)
    shop_store_comments = models.TextField(blank=True)
    
    # Store/Storage Section
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    store_current_quantity = models.IntegerField(null=True, blank=True)
    quantity_taken_from_store = models.IntegerField(null=True, blank=True)
    remaining_store_quantity = models.IntegerField(null=True, blank=True)
    store_photo = models.ImageField(upload_to='store_photos/', null=True, blank=True)
    store_comments = models.TextField(blank=True)
    
    # Main Store Section
    main_store = models.ForeignKey(MainStore, on_delete=models.CASCADE, null=True, blank=True)
    main_store_quantity = models.IntegerField(null=True, blank=True)
    quantity_taken_from_main_store = models.IntegerField(null=True, blank=True)
    remaining_main_store_quantity = models.IntegerField(null=True, blank=True)
    main_store_photo = models.ImageField(upload_to='main_store_photos/', null=True, blank=True)
    main_store_comments = models.TextField(blank=True)
    
    # Final quantities
    quantity_taken_from_main = models.IntegerField(null=True, blank=True)
    final_shop_quantity = models.IntegerField(null=True, blank=True)
    final_store_quantity = models.IntegerField(null=True, blank=True)
    
    # General fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report {self.id} - {self.shop.name} - {self.product.name}"

    class Meta:
        ordering = ['-created_at']


class Inventory(models.Model):
    """Model for tracking current inventory levels"""
    location_type_choices = [
        ('shop', 'Shop'),
        ('store', 'Store'),
        ('main_store', 'Main Store')
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location_type = models.CharField(max_length=20, choices=location_type_choices)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)
    main_store = models.ForeignKey(MainStore, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    last_report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = [['product', 'location_type', 'shop', 'main_store']]

    def __str__(self):
        location = self.shop.name if self.shop else self.main_store.name
        return f"{self.product.name} at {location}"