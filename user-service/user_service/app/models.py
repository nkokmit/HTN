from django.db import models

class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    STAFF = "STAFF", "Staff"
    CUSTOMER = "CUSTOMER", "Customer"

class UserAccount(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)

class StaffAction(models.Model):
    product_id = models.IntegerField()
    action = models.CharField(max_length=50)
    note = models.CharField(max_length=255, blank=True)

class ManagerNote(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)

# --- THÊM MODEL CHUẨN ĐỊA CHỈ DƯỚI ĐÂY ---
class UserAddress(models.Model):
    # Liên kết trực tiếp tới UserAccount của bạn
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255, verbose_name="Tên người nhận")
    phone_number = models.CharField(max_length=20, verbose_name="Số điện thoại nhận hàng")
    city = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố")
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện")
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã")
    detail_address = models.CharField(max_length=255, verbose_name="Địa chỉ chi tiết (Số nhà, đường...)")
    is_default = models.BooleanField(default=False, verbose_name="Địa chỉ mặc định")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        # Nếu đặt địa chỉ này làm mặc định, tự động bỏ mặc định các địa chỉ khác của user này
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)