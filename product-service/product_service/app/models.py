from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Book(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="book")
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20)


class Electronics(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="electronics")
    brand = models.CharField(max_length=100)
    warranty = models.IntegerField()


class Fashion(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="fashion")
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)


class Home(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="home")
    material = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    feature = models.CharField(max_length=255)


class Toy(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="toy")
    age_range = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    safety_note = models.CharField(max_length=255)


class Health(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="health")
    usage = models.CharField(max_length=255)
    origin = models.CharField(max_length=100)
    note = models.CharField(max_length=255)


