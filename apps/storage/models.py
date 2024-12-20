
class Location(models.Model):
    LOCATION_TYPES = (
        ('STORE', 'Retail Store'),
        ('WAREHOUSE', 'Warehouse'),
        ('STORAGE', 'Storage Facility'),
    )
    
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    last_checked = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Inventories"
        unique_together = ['product', 'location']

    def __str__(self):
        return f"{self.product.name} at {self.location.name}"

class InventoryCheck(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    rep = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    check_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Check by {self.rep.username} at {self.location.name}"

class InventoryCheckItem(models.Model):
    inventory_check = models.ForeignKey(InventoryCheck, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    expected_quantity = models.IntegerField()
    actual_quantity = models.IntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} - Check #{self.inventory_check.id}"

class StockRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FULFILLED', 'Fulfilled'),
    )

    requester = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='stock_requests')
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='outgoing_requests')
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='incoming_requests')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Request #{self.id} - {self.product.name}"



