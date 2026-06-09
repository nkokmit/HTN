from decimal import Decimal

from django.db import migrations, models


def forwards(apps, schema_editor):
    CartItem = apps.get_model('app', 'CartItem')
    for item in CartItem.objects.all():
        if item.product_id is None:
            item.product_id = item.book_id or item.clothes_id
        if not item.product_type:
            if item.item_type == 'CLOTHES':
                item.product_type = 'FASHION'
            else:
                item.product_type = item.item_type or 'BOOK'
        if not item.product_name:
            item.product_name = ''
        if item.unit_price is None:
            item.unit_price = Decimal('0.00')
        item.save(update_fields=['product_id', 'product_type', 'product_name', 'unit_price'])


def backwards(apps, schema_editor):
    CartItem = apps.get_model('app', 'CartItem')
    for item in CartItem.objects.all():
        if item.product_type == 'FASHION':
            item.item_type = 'CLOTHES'
        elif item.product_type:
            item.item_type = item.product_type
        if item.product_id:
            if item.product_type == 'BOOK':
                item.book_id = item.product_id
            elif item.product_type == 'FASHION':
                item.clothes_id = item.product_id
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='product_id',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_type',
            field=models.CharField(choices=[('BOOK', 'BOOK'), ('ELECTRONICS', 'ELECTRONICS'), ('FASHION', 'FASHION')], default='BOOK', max_length=20),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='item_type',
            field=models.CharField(choices=[('BOOK', 'BOOK'), ('CLOTHES', 'CLOTHES'), ('ELECTRONICS', 'ELECTRONICS'), ('FASHION', 'FASHION')], default='BOOK', max_length=20),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.RunPython(forwards, backwards),
    ]