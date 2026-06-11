from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_cart_item_id_and_subtotal'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_phone',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_city',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='note',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
