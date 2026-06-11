from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    STAFF = "STAFF", "Staff"
    CUSTOMER = "CUSTOMER", "Customer"


class UserAccount(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)


class StaffAction(models.Model):
    product_id = models.IntegerField()
    action = models.CharField(max_length=50)
    note = models.CharField(max_length=255, blank=True)


class ManagerNote(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)