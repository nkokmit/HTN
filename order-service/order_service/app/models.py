from django.db import models


class Order(models.Model):
    # id mặc định được Django tự tạo làm Khóa chính (Primary Key)
    user_id = models.IntegerField()
    status = models.CharField(max_length=50)
    # double trong database được map chính xác nhất qua DecimalField trong Django để tránh sai số tiền tệ
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_address = models.TextField()
    shipping_phone = models.CharField(max_length=10)
    shipping_city = models.CharField(max_length=20)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    # Khóa chính phức hợp (Composite Key) gồm order_id và product_id trong hình
    # được xử lý chuẩn trong Django bằng unique_together
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        # Đồng bộ hóa khóa chính phức hợp: Đảm bảo một cặp (order, product) là duy nhất
        unique_together = (('order', 'product_id'),)
        # Khai báo tên bảng là 'order_item' giống hệt trong hình (tùy chọn)
        db_table = 'order_item'
