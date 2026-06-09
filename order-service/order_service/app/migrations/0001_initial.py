from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pay_method', models.CharField(max_length=50)),
                ('ship_method', models.CharField(max_length=50)),
                ('status', models.CharField(default='CREATED', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_item_id', models.IntegerField(blank=True, null=True)),
                ('product_id', models.IntegerField(blank=True, null=True, db_index=True)),
                ('product_type', models.CharField(choices=[('BOOK','BOOK'),('ELECTRONICS','ELECTRONICS'),('FASHION','FASHION')], default='BOOK', max_length=20)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=12)),
                ('order', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='items', to='app.order')),
            ],
        ),
    ]
