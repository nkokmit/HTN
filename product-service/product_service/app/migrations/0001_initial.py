from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="")),
                ("image_url", models.URLField(blank=True, null=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("stock", models.IntegerField(default=0)),
                ("category", models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("author", models.CharField(max_length=255)),
                ("publisher", models.CharField(blank=True, default="", max_length=255)),
                ("isbn", models.CharField(blank=True, default="", max_length=50)),
                ("product", models.OneToOneField(on_delete=models.CASCADE, related_name="book", to="app.product")),
            ],
        ),
        migrations.CreateModel(
            name="Electronics",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("brand", models.CharField(blank=True, default="", max_length=255)),
                ("warranty", models.PositiveIntegerField(default=0)),
                ("product", models.OneToOneField(on_delete=models.CASCADE, related_name="electronics", to="app.product")),
            ],
        ),
        migrations.CreateModel(
            name="Fashion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("size", models.CharField(blank=True, default="", max_length=50)),
                ("color", models.CharField(blank=True, default="", max_length=50)),
                ("product", models.OneToOneField(on_delete=models.CASCADE, related_name="fashion", to="app.product")),
            ],
        ),
    ]
