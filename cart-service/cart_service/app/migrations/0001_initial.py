from django.db import migrations, models
from django.db.models import deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('BOOK', 'BOOK'), ('CLOTHES', 'CLOTHES')], default='BOOK', max_length=20)),
                ('book_id', models.IntegerField(blank=True, null=True)),
                ('clothes_id', models.IntegerField(blank=True, null=True)),
                ('clothes_variant_id', models.IntegerField(blank=True, null=True)),
                ('size', models.CharField(blank=True, max_length=50, null=True)),
                ('color', models.CharField(blank=True, max_length=50, null=True)),
                ('quantity', models.IntegerField()),
                ('cart', models.ForeignKey(on_delete=deletion.CASCADE, to='app.cart')),
            ],
        ),
    ]
