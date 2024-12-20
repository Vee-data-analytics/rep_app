from django.db import models
import uuid
from users.models import User
from reptrack_trace.models import *

class Report(models.Model):
    """Model for storing representative reports"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    representative = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reports_as_representative'  # Updated
    )
    shop = models.ForeignKey(
        Shop, 
        on_delete=models.CASCADE, 
        related_name='reports_for_shop'  # Updated
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reports_for_product'  # Updated
    )
    main_store = models.ForeignKey(
        MainStore, 
        on_delete=models.CASCADE, 
        related_name='reports_for_main_store',  # Updated
        null=True, 
        blank=True
    )
    
    # Shop section
    shop_current_quantity = models.IntegerField()
    needs_topup = models.BooleanField()
    desired_quantity = models.IntegerField(null=True, blank=True)
    topup_quantity = models.IntegerField(null=True, blank=True)
    shop_photo = models.ImageField(upload_to='shop_photos/')
    shop_comments = models.TextField(blank=True)
    
    # Shop-Store section
    store_manager_confirmed = models.BooleanField(default=False)
    store_current_quantity = models.IntegerField(null=True, blank=True)
    has_sufficient_stock = models.BooleanField(null=True)
    quantity_taken_from_store = models.IntegerField(null=True, blank=True)
    remaining_store_quantity = models.IntegerField(null=True, blank=True)
    store_photo = models.ImageField(upload_to='store_photos/', null=True, blank=True)
    store_comments = models.TextField(blank=True)
    
    # Main Store section
    main_store_quantity = models.IntegerField(null=True, blank=True)
    quantity_taken_from_main = models.IntegerField(null=True, blank=True)
    remaining_main_quantity = models.IntegerField(null=True, blank=True)
    main_store_photo = models.ImageField(upload_to='main_store_photos/', null=True, blank=True)
    main_store_comments = models.TextField(blank=True)
    
    # Final quantities after restocking
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
