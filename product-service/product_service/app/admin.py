from django.contrib import admin

from .models import Book, Category, Electronics, Fashion, Health, Home, Product, Toy


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Book)
admin.site.register(Electronics)
admin.site.register(Fashion)
admin.site.register(Home)
admin.site.register(Toy)
admin.site.register(Health)
