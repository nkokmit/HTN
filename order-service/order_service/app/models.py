from django.db import models


class Order(models.Model):
    # id mặc định được Django tự tạo làm Khóa chính (Primary Key)
    customer_id = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pay_method = models.CharField(max_length=50)
    ship_method = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='CREATED')
    # double trong database được map chính xác nhất qua DecimalField trong Django để tránh sai số tiền tệ
    shipping_address = models.TextField(default='')
    shipping_phone = models.CharField(max_length=20, default='')
    shipping_city = models.CharField(max_length=100, default='')
    note = models.TextField(blank=True, null=True, default='')


class OrderItem(models.Model):
    # Khóa chính phức hợp (Composite Key) gồm order_id và product_id trong hình
    # được xử lý chuẩn trong Django bằng unique_together
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    product_type = models.CharField(max_length=20, default='BOOK')
    title = models.CharField(max_length=255, blank=True, default='')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        # Đồng bộ hóa khóa chính phức hợp: Đảm bảo một cặp (order, product) là duy nhất
        unique_together = (('order', 'product_id'),)
        # Khai báo tên bảng là 'order_item' giống hệt trong hình (tùy chọn)
        db_table = 'order_item'
