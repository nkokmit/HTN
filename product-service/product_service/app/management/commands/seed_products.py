from django.core.management.base import BaseCommand
from django.db import transaction
import random
from ...models import Category, Product, Book, Electronics, Fashion, Home, Toy, Health

N = 100

BOOK_TITLES = [
    'Hành trình lập trình', 'Thiết kế hệ thống', 'Python nâng cao', 'Thuật toán thực chiến',
    'Kiến trúc phần mềm', 'Kỹ năng mềm cho dev', 'Lập trình web bằng Django', 'Cẩm nang DevOps'
]

ELECTRONICS_NAMES = [
    'Smartwatch AMOLED', 'Tai nghe ANC', 'Camera mini', 'Loa bluetooth', 'Sạc nhanh 65W', 'Laptop 14"'
]

FASHION_NAMES = [
    'Sneaker thời trang', 'Áo phông cotton', 'Quần jeans', 'Váy nữ', 'Áo khoác nhẹ'
]

HOME_NAMES = [
    'Bộ nồi chống dính', 'Chăn gối cao cấp', 'Đèn học LED', 'Máy xay sinh tố', 'Bàn ủi hơi nước'
]

TOY_NAMES = [
    'Bộ xếp hình', 'Đồ chơi phát triển', 'Búp bê cỡ lớn', 'Xe điều khiển', 'Bộ ghép hình'
]

HEALTH_NAMES = [
    'Vitamin tổng hợp', 'Bàn chải điện', 'Bộ chăm sóc da', 'Nước rửa tay khô', 'Cân sức khỏe'
]

CATEGORY_MAP = {
    'Books': BOOK_TITLES,
    'Electronics': ELECTRONICS_NAMES,
    'Fashion': FASHION_NAMES,
    'Home': HOME_NAMES,
    'Toys': TOY_NAMES,
    'Health': HEALTH_NAMES,
}

class Command(BaseCommand):
    help = 'Seed the database with sample products (creates categories and N products)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=N, help='Number of products to create')

    @transaction.atomic
    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f"Seeding database with {count} products...")

        # create categories
        categories = {}
        for name in CATEGORY_MAP.keys():
            cat, _ = Category.objects.get_or_create(name=name)
            categories[name] = cat
        self.stdout.write(f"Categories: {', '.join(categories.keys())}")

        # create products
        created = 0
        for i in range(count):
            # pick a category
            cat_name = random.choice(list(CATEGORY_MAP.keys()))
            cat = categories[cat_name]

            if cat_name == 'Books':
                base = random.choice(BOOK_TITLES)
            elif cat_name == 'Electronics':
                base = random.choice(ELECTRONICS_NAMES)
            elif cat_name == 'Fashion':
                base = random.choice(FASHION_NAMES)
            elif cat_name == 'Home':
                base = random.choice(HOME_NAMES)
            elif cat_name == 'Toys':
                base = random.choice(TOY_NAMES)
            else:
                base = random.choice(HEALTH_NAMES)

            name = f"{base} - mẫu {i+1}"
            price = round(random.uniform(99.0, 1999.0), 2)
            stock = random.randint(0, 500)

            prod = Product.objects.create(name=name, price=price, stock=stock, category=cat)

            # create subtype data
            if cat_name == 'Books':
                Book.objects.create(product=prod, author='Tác giả '+str(random.randint(1,20)), publisher='NXB A', isbn=str(9780000000000 + i))
            elif cat_name == 'Electronics':
                Electronics.objects.create(product=prod, brand='Brand'+str(random.randint(1,10)), warranty=random.choice([6,12,24]))
            elif cat_name == 'Fashion':
                Fashion.objects.create(product=prod, size=random.choice(['S','M','L','XL']), color=random.choice(['Đen','Trắng','Xanh','Đỏ']))
            elif cat_name == 'Home':
                Home.objects.create(
                    product=prod,
                    material=random.choice(['Inox', 'Gỗ', 'Nhựa ABS', 'Vải cotton']),
                    brand=random.choice(['LifePro', 'Sunhouse', 'LocknLock', 'Koenic']),
                    feature=random.choice(['Tiết kiệm diện tích', 'Chống dính', 'Bền đẹp', 'Dễ vệ sinh']),
                )
            elif cat_name == 'Toys':
                Toy.objects.create(
                    product=prod,
                    age_range=random.choice(['3+', '5+', '7+', '10+']),
                    material=random.choice(['Nhựa an toàn', 'Gỗ', 'Silicon', 'Vải']),
                    safety_note=random.choice(['Không chứa BPA', 'Đạt chuẩn an toàn', 'Bo tròn góc cạnh', 'Phù hợp trẻ em']),
                )
            elif cat_name == 'Health':
                Health.objects.create(
                    product=prod,
                    usage=random.choice(['Dùng hằng ngày', 'Bổ sung sức khỏe', 'Chăm sóc cá nhân', 'Hỗ trợ thể chất']),
                    origin=random.choice(['Việt Nam', 'Nhật Bản', 'Hàn Quốc', 'Hoa Kỳ']),
                    note=random.choice(['HSD in trên bao bì', 'Sử dụng theo hướng dẫn', 'Bảo quản nơi khô ráo', 'Dùng đúng liều lượng']),
                )

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} products."))