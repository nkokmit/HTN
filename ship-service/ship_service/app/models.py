from django.db import models

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_id = models.IntegerField(db_index=True)
    method = models.CharField(max_length=50)
    address = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='CREATED')
    tracking_number = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
