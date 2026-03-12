from django.db import models

class Rating(models.Model):
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    score = models.IntegerField()
    comment = models.CharField(max_length=500, blank=True)
