from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="product_type",
            field=models.CharField(default="BOOK", max_length=20),
        ),
    ]
