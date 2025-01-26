from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from users.models import User 
from PIL import Image
from PIL.ExifTags import TAGS
import uuid

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



class ShopStore(models.Model):
    """Model to represent the relationship between a Shop and a Store"""
    shop = models.OneToOneField(
        Shop, 
        on_delete=models.CASCADE, 
        related_name='shop_stores',
        unique=True
    )
    quantity_taken = models.IntegerField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"{self.shop.name}"
    
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
    shop_photo_taken_at = models.DateTimeField(null=True, blank=True)  
    
    # Shop-Stores Section
    
    shop_store_manager_confirmed = models.BooleanField(default=False)
    shop_store_current_quantity = models.IntegerField(null=True, blank=True)
    shop_store_has_sufficient_stock = models.BooleanField(null=True)
    quantity_taken_from_shop_store = models.IntegerField(null=True, blank=True)
    remaining_shop_store_quantity = models.IntegerField(null=True, blank=True)
    shop_store_photo = models.ImageField(upload_to='shop_store_photos/', null=True, blank=True)
    shop_store_comments = models.TextField(blank=True)
    was_shop_updated = models.BooleanField(null=True, blank=True)
    shop_photo_update = models.ImageField(upload_to='shop_photos/', null=True, blank=True)
    shop_update_quantity = models.IntegerField(null=True, blank=True)
    shop_store_photo_taken_at = models.DateTimeField(null=True, blank=True)
    shop_photo_update_taken_at = models.DateTimeField(null=True, blank=True)
    
    # Main Store Section
    main_store = models.ForeignKey(MainStore, on_delete=models.CASCADE, null=True, blank=True)
    main_store_quantity = models.IntegerField(null=True, blank=True)
    quantity_taken_from_main_store = models.IntegerField(null=True, blank=True)
    remaining_main_store_quantity = models.IntegerField(null=True, blank=True)
    main_store_photo = models.ImageField(upload_to='main_store_photos/', null=True, blank=True)
    main_store_comments = models.TextField(blank=True)
    shop_store_current_quantity = models.IntegerField(null=True, blank=True)
    shop_quantity = models.IntegerField(null=True, blank=True)
    was_shop_stores_updated = models.BooleanField(null=True, blank=True)
    was_shop_m_updated = models.BooleanField(null=True, blank=True)
    current_shop_store_photo = models.ImageField(upload_to='store_photos/', null=True, blank=True)
    current_shop_store_photo_taken_at=models.DateTimeField(null=True, blank=True)
    current_shop_photo = models.ImageField(upload_to='store_photos/', null=True, blank=True)
    current_shop_photo_taken_at=models.DateTimeField(null=True, blank=True)
    delivered_to_shop_stores = models.IntegerField(null=True,blank=True)
    quantity_in_shopstores = models.IntegerField(null=True, blank=True)
    delivered_to_shop = models.IntegerField(null=True,blank=True)
    total_quantity_in_shop   = models.IntegerField(null=True,blank=True)
    main_store_photo_taken_at = models.DateTimeField(null=True, blank=True)
     
    # Final quantities
    quantity_taken_from_main = models.IntegerField(null=True, blank=True)
    final_shop_quantity = models.IntegerField(null=True, blank=True)
    final_store_quantity = models.IntegerField(null=True, blank=True)
    
    # General fields    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    def calculate_final_quantities(self):
        try:
            if self.report_stage == 'main_store':
                self.final_shop_quantity = int(self.total_quantity_in_shop) if self.total_quantity_in_shop is not None else None
                self.final_store_quantity = int(self.main_store_quantity) if self.main_store_quantity is not None else None
            elif self.report_stage == 'shop_store':
                self.final_shop_quantity = int(self.shop_update_quantity) if self.shop_update_quantity is not None else None
                self.final_store_quantity = int(self.shop_store_current_quantity) if self.shop_store_current_quantity is not None else None
            elif self.report_stage == 'shop':
                self.final_shop_quantity = int(self.shop_current_quantity) if self.shop_current_quantity is not None else None
                self.final_store_quantity = None
            
            self.save()
        except (TypeError, ValueError):
            # Handle conversion errors
            return False

    def save(self, *args, **kwargs):
        """Override save method to store calculated topup_quantity."""
        self.topup_quantity = self.calculate_topup_quantity()
        super().save(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report {self.id} - {self.shop.name} - {self.product.name}"

    class Meta:
        ordering = ['-created_at']
    
    
    def extract_image_metadata(self, image_field):
      """Extract EXIF metadata from an image field."""
      try:
          with Image.open(image_field) as img:
              exif_data = img._getexif()
              if exif_data:
                  for tag_id, value in exif_data.items():
                      tag = TAGS.get(tag_id, tag_id)
                      if tag == 'DateTimeOriginal':
                          # Convert EXIF date string to datetime object
                          from datetime import datetime
                          return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
      except (AttributeError, KeyError, ValueError):
          # Handle cases where EXIF data is missing or invalid
          return None

    def save(self, *args, **kwargs):
        """Override save method to extract image metadata."""
        # Extract metadata for shop_photo
        if self.shop_photo and not self.shop_photo_taken_at:
            self.shop_photo_taken_at = self.extract_image_metadata(self.shop_photo)
        
        if self.current_shop_photo_taken_at and not self.current_shop_photo_taken_at:
            self.current_shop_photo_taken_at  = self.extract_image_metadata(current_shop_photo)
        
        if self.shop_store_photo_taken_at and not self.shop_photo_update_taken_at:
            self.shop_photo_update_taken_at = self.extract_image_metadata(shop_photo_update)
        
        # Extract metadata for shop_store_photo
        if self.shop_store_photo and not self.shop_store_photo_taken_at:
            self.shop_store_photo_taken_at = self.extract_image_metadata(self.shop_store_photo)
            
        if self.current_shop_store_photo and not self.current_shop_store_photo_taken_at:
            self.current_shop_store_photo_taken_at = self.extract_image_metadata(self.current_shop_store_photo)
        
        # Extract metadata for main_store_photo
        if self.main_store_photo and not self.main_store_photo_taken_at:
            self.main_store_photo_taken_at = self.extract_image_metadata(self.main_store_photo)
        
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