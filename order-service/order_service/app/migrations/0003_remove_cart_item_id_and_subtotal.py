from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_simplify_order_item_product_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="cart_item_id",
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="subtotal",
        ),
    ]
