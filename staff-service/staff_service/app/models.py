from django.db import models


class StaffAction(models.Model):
	book_id = models.IntegerField()
	action = models.CharField(max_length=50)
	note = models.CharField(max_length=255, blank=True)

