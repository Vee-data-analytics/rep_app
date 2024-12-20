from django.db import models
from apps.site_shop.models import Product, Location
from apps.users.models import CustomUser

class WarehouseZone(models.Model):
    warehouse = models.ForeignKey(Location, on_delete=models.CASCADE, limit_choices_to={'location_type': 'WAREHOUSE'})
    name = models.CharField(max_length=100)  # e.g., "Zone A", "Bulk Storage", "Cold Storage"
    description = models.TextField(blank=True)
    temperature_controlled = models.BooleanField(default=False)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacity in cubic meters")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"

class WarehouseShelf(models.Model):
    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE)
    shelf_number = models.CharField(max_length=20)
    capacity = models.IntegerField(help_text="Maximum number of items")
    current_utilization = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Warehouse Shelves"
        unique_together = ['zone', 'shelf_number']

    def __str__(self):
        return f"{self.zone.name} - Shelf {self.shelf_number}"

class WarehouseInventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shelf = models.ForeignKey(WarehouseShelf, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    batch_number = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    last_checked = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Warehouse Inventories"

    def __str__(self):
        return f"{self.product.name} - {self.shelf.shelf_number}"

class WarehouseTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('RECEIVING', 'Receiving'),
        ('SHIPPING', 'Shipping'),
        ('TRANSFER', 'Internal Transfer'),
        ('ADJUSTMENT', 'Inventory Adjustment'),
    )

    warehouse = models.ForeignKey(Location, on_delete=models.CASCADE, limit_choices_to={'location_type': 'WAREHOUSE'})
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_number = models.CharField(max_length=50, unique=True)
    handler = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.reference_number} - {self.transaction_type}"

class WarehouseTransactionItem(models.Model):
    transaction = models.ForeignKey(WarehouseTransaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    source_shelf = models.ForeignKey(WarehouseShelf, on_delete=models.CASCADE, related_name='source_transactions', null=True)
    destination_shelf = models.ForeignKey(WarehouseShelf, on_delete=models.CASCADE, related_name='destination_transactions', null=True)

    def __str__(self):
        return f"{self.transaction.reference_number} - {self.product.name}"
