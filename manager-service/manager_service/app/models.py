from django.db import models


class ManagerNote(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)

class ManagerNote(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
