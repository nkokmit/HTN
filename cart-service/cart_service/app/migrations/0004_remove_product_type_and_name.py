from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_remove_legacy_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cartitem",
            name="product_type",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="product_name",
        ),
    ]
