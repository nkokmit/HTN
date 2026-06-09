from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_product_centric_cart_item"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cartitem",
            name="item_type",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="book_id",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="clothes_id",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="clothes_variant_id",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="size",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="color",
        ),
    ]
