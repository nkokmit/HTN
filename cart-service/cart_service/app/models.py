from django.db import models

class Cart(models.Model):
    customer_id = models.IntegerField()


class CartItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('BOOK', 'BOOK'),
        ('CLOTHES', 'CLOTHES'),
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='BOOK')
    book_id = models.IntegerField(null=True, blank=True)
    clothes_id = models.IntegerField(null=True, blank=True)
    clothes_variant_id = models.IntegerField(null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField()
