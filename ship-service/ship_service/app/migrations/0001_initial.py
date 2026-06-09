# Generated migration for initial Shipment model with all fields

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField(db_index=True)),
                ('method', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('status', models.CharField(choices=[('CREATED', 'Created'), ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('IN_TRANSIT', 'In Transit'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='CREATED', max_length=50)),
                ('tracking_number', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
