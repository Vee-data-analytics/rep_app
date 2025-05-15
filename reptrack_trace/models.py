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



class Product(models.Model):
    """Model for storing product information"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Report(models.Model):
    """
    Model for storing representative reports, preserving original 'Shop' field names
    where possible, removing old sections, and adding new 'Sales Stock File'
    and 'Merchandising' details.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    representative = models.ForeignKey(User, on_delete=models.CASCADE) 
    
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    
    shop_current_quantity = models.IntegerField(
        help_text="Current quantity physically counted in the shop (Maps to 'Current Quantity Found' in PDF)."
    )
    
    stock_file_photo = models.ImageField(
        upload_to='stock_file_photos/', 
        help_text="Picture of the physical stock file/sheet (Previously 'Shop Shelf Photo')."
    )

    shop_comments = models.TextField(
        blank=True,
        help_text="Comment or resolution for any stock discrepancy found (Maps to 'Comment/Resolution' in PDF)."
    )

    # Option 1: Keep as a database field, but make it nullable and blank-able
    discrepancy = models.IntegerField(
        null=True, blank=True,
        help_text="Auto calculated discrepancy between stock file and current quantity"
    )

    stock_file_quantity = models.IntegerField(
        null=True,
        help_text="Quantity written on the stock file."
    )
    
    po_photo = models.ImageField(
        upload_to='po_photos/',
        null=True, blank=True,
        help_text="Take a picture of the P.O if Applicable"
    )
    
    shop_photo_taken_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    # --- Merchandizing Section (Added from PDF) ---
    
    # Before Photos
    before_merch_photo_1 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    before_merch_photo_2 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    before_merch_photo_3 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    before_merch_photo_4 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    before_merch_photo_5 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)

    # After Photos
    after_merch_photo_1 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    after_merch_photo_2 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    after_merch_photo_3 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    after_merch_photo_4 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    after_merch_photo_5 = models.ImageField(upload_to='merch_photos/', null=True, blank=True)
    
    # Merchandising Comment
    merchandising_comment = models.TextField(blank=True, help_text="Comments on merchandising actions taken.")

    # --- General fields ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)



    def __str__(self):
        return f"Report {self.id} for {self.shop.name} - {self.product.name}"

    class Meta:
        ordering = ['-created_at']
   

    
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
        except (AttributeError, KeyError, ValueError, TypeError):
            return None

    def __str__(self):
        return f"Report {self.id} - {self.shop.name} - {self.product.name}"

    class Meta:
        ordering = ['-created_at']
