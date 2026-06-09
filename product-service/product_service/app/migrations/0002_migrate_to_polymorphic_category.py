from django.db import migrations, models
import django.db.models.deletion


def forwards_populate_category(apps, schema_editor):
    Product = apps.get_model("app", "Product")
    Category = apps.get_model("app", "Category")

    for product in Product.objects.all().iterator():
        category_name = (product.legacy_category or "").strip() or "UNKNOWN"
        category, _ = Category.objects.get_or_create(name=category_name.upper())
        product.category_ref = category
        product.save(update_fields=["category_ref"])


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.RenameField(
            model_name="product",
            old_name="category",
            new_name="legacy_category",
        ),
        migrations.AddField(
            model_name="product",
            name="category_ref",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name="products", to="app.category"),
        ),
        migrations.RunPython(forwards_populate_category, noop_reverse),
        migrations.AlterField(
            model_name="product",
            name="category_ref",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="products", to="app.category"),
        ),
        migrations.RemoveField(
            model_name="product",
            name="legacy_category",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="category_ref",
            new_name="category",
        ),
        migrations.RemoveField(
            model_name="product",
            name="description",
        ),
        migrations.RemoveField(
            model_name="product",
            name="image_url",
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name="product",
            name="stock",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="book",
            name="publisher",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="electronics",
            name="brand",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="electronics",
            name="warranty",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="fashion",
            name="size",
            field=models.CharField(max_length=10),
        ),
    ]
