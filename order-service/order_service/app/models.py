from django.db import models


class Order(models.Model):
    customer_id = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pay_method = models.CharField(max_length=50)
    ship_method = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='CREATED')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    cart_item_id = models.IntegerField(null=True, blank=True)
    book_id = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
