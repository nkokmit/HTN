from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_migrate_to_polymorphic_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="Home",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("material", models.CharField(max_length=100)),
                ("brand", models.CharField(max_length=100)),
                ("feature", models.CharField(max_length=255)),
                ("product", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="home", to="app.product")),
            ],
        ),
        migrations.CreateModel(
            name="Toy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("age_range", models.CharField(max_length=50)),
                ("material", models.CharField(max_length=100)),
                ("safety_note", models.CharField(max_length=255)),
                ("product", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="toy", to="app.product")),
            ],
        ),
        migrations.CreateModel(
            name="Health",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("usage", models.CharField(max_length=255)),
                ("origin", models.CharField(max_length=100)),
                ("note", models.CharField(max_length=255)),
                ("product", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="health", to="app.product")),
            ],
        ),
    ]
