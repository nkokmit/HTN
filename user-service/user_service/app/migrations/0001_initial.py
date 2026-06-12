from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StaffAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField()),
                ('action', models.CharField(max_length=50)),
                ('note', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('STAFF', 'Staff'), ('CUSTOMER', 'Customer')], default='CUSTOMER', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='Tên người nhận')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Số điện thoại nhận hàng')),
                ('city', models.CharField(max_length=100, verbose_name='Tỉnh/Thành phố')),
                ('district', models.CharField(max_length=100, verbose_name='Quận/Huyện')),
                ('ward', models.CharField(max_length=100, verbose_name='Phường/Xã')),
                ('detail_address', models.CharField(max_length=255, verbose_name='Địa chỉ chi tiết (Số nhà, đường...)')),
                ('is_default', models.BooleanField(default=False, verbose_name='Địa chỉ mặc định')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='app.useraccount')),
            ],
            options={
                'ordering': ['-is_default', '-created_at'],
            },
        ),
    ]