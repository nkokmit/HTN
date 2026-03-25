from django.db import models
from django.core.validators import MinValueValidator


class Clothes(models.Model):
    """Main clothes product model"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ClothesVariant(models.Model):
    """Variant for each clothes product (size + color combination)"""
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=50)  # XS, S, M, L, XL, XXL, etc.
    color = models.CharField(max_length=50)  # Red, Blue, Black, White, etc.
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('clothes', 'size', 'color')
        ordering = ['clothes', 'size', 'color']

    def __str__(self):
        return f"{self.clothes.name} - {self.size}/{self.color} ({self.stock})"
