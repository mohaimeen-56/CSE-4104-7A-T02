import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Ensure app package is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zoneinfo import ZoneInfo

from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.models.product import Product
from app.models.region import Region
from app.models.sale import Sale
from app.models.notification import Notification
from app.core.security import get_password_hash

DHAKA_TZ = ZoneInfo("Asia/Dhaka")
# Business-hour weighting for synthetic sale times: lunchtime and evening peaks.
HOUR_WEIGHTS = {h: 1 for h in range(24)}
for h in (10, 11, 12, 13, 17, 18, 19, 20):
    HOUR_WEIGHTS[h] = 6
for h in (9, 14, 15, 16, 21):
    HOUR_WEIGHTS[h] = 3
for h in list(range(0, 8)) + [22, 23]:
    HOUR_WEIGHTS[h] = 1


def seed_database():
    print("Using existing database schema (run 'alembic upgrade head' first if tables are missing)...")
    db = SessionLocal()

    try:
        # 1. Clear existing data in reverse dependency order
        print("Cleaning up old records...")
        db.query(Notification).delete()
        db.query(Sale).delete()
        db.query(Product).delete()
        db.query(Region).delete()
        db.query(User).delete()
        db.commit()

        # 2. Seed Users
        print("Seeding demo users...")
        users = [
            User(
                name="Mohaimeen Islam Pial",
                email="pial@example.com",
                password_hash=get_password_hash("admin123"),
                role="admin",
                created_at=datetime(2026, 1, 1, 10, 0)
            ),
            User(
                name="Sk Mesbaul Arefin",
                email="mesbaul@example.com",
                password_hash=get_password_hash("manager123"),
                role="manager",
                created_at=datetime(2026, 1, 2, 10, 0)
            ),
            User(
                name="Sumaiya Akter",
                email="sumaiya@example.com",
                password_hash=get_password_hash("manager123"),
                role="manager",
                created_at=datetime(2026, 1, 3, 10, 0)
            ),
            User(
                name="Afia Maliha Priota",
                email="priota@example.com",
                password_hash=get_password_hash("viewer123"),
                role="viewer",
                created_at=datetime(2026, 1, 4, 10, 0)
            ),
        ]
        db.add_all(users)
        db.commit()
        for u in users:
            db.refresh(u)

        # 3. Seed Regions
        print("Seeding regions...")
        regions = [
            Region(name="Dhaka", country="Bangladesh"),
            Region(name="Chittagong", country="Bangladesh"),
            Region(name="Khulna", country="Bangladesh"),
            Region(name="Sylhet", country="Bangladesh"),
            Region(name="Rajshahi", country="Bangladesh"),
        ]
        db.add_all(regions)
        db.commit()
        for r in regions:
            db.refresh(r)

        # 4. Seed Products
        print("Seeding products...")
        products = [
            Product(name="iPhone 15", category="Phone", subcategory="Smartphone", brand="Apple", sku="APL-IP15-BLK",
                     description="Latest flagship smartphone with dynamic island", price=Decimal("87500.00"), cost=Decimal("68000.00"), stock=45),
            Product(name="ThinkPad X1 Carbon", category="Laptop", subcategory="Business Laptop", brand="Lenovo", sku="LNV-X1C-14",
                     description="High-end carbon-fiber business laptop", price=Decimal("142000.00"), cost=Decimal("112000.00"), stock=28),
            Product(name="Galaxy Tab S9", category="Tablet", subcategory="Android Tablet", brand="Samsung", sku="SAM-TABS9-256",
                     description="Dynamic AMOLED 120Hz display with S-Pen", price=Decimal("62000.00"), cost=Decimal("48500.00"), stock=16, production_level="low"),  # Low stock < 20
            Product(name="AirPods Pro", category="Audio", subcategory="Earbuds", brand="Apple", sku="APL-APP-2G",
                     description="Active noise cancellation wireless earbuds", price=Decimal("24500.00"), cost=Decimal("18000.00"), stock=80),
            Product(name="Dell XPS 15", category="Laptop", subcategory="Creator Laptop", brand="Dell", sku="DEL-XPS15-OLED",
                     description="Premium 4K OLED creator laptop", price=Decimal("185000.00"), cost=Decimal("149000.00"), stock=12, production_level="low"),  # Low stock < 20
            Product(name="Sony WH-1000XM5", category="Audio", subcategory="Headphones", brand="Sony", sku="SNY-WH1000XM5",
                     description="Industry-leading wireless ANC headphones", price=Decimal("38000.00"), cost=Decimal("29000.00"), stock=35),
            Product(name="Office Ergonomic Chair", category="Furniture", subcategory="Seating", brand="ErgoLine", sku="ERG-CHR-MESH",
                     description="Ergonomic mesh chair with lumbar support", price=Decimal("16500.00"), cost=Decimal("11500.00"), stock=65, production_level="high"),
            Product(name="Smart LED Desk Lamp", category="Furniture", subcategory="Lighting", brand="Xiaomi", sku="XMI-LAMP-LED2",
                     description="Multi-angle dimmable color-temp desk lamp", price=Decimal("3200.00"), cost=Decimal("2100.00"), stock=120, production_level="high"),
            Product(name="Logitech MX Master 3S", category="Electronics", subcategory="Peripherals", brand="Logitech", sku="LOG-MXM3S",
                     description="High precision quiet-click wireless mouse", price=Decimal("11500.00"), cost=Decimal("8200.00"), stock=90),
            Product(name="Samsung 4K Monitor 27\"", category="Electronics", subcategory="Monitors", brand="Samsung", sku="SAM-MON27-4K",
                     description="Ultra HD IPS professional monitor", price=Decimal("34000.00"), cost=Decimal("26500.00"), stock=25),
        ]
        db.add_all(products)
        db.commit()
        for p in products:
            db.refresh(p)

        # 5. Seed Historical Multi-Month Sales Records (January to August 2026)
        print("Seeding realistic multi-month sales transactions...")
        sales_records = []
        random.seed(42)

        # Product unit prices mapping (BDT)
        prices = {
            "iPhone 15": Decimal("87500.00"),
            "ThinkPad X1 Carbon": Decimal("142000.00"),
            "Galaxy Tab S9": Decimal("62000.00"),
            "AirPods Pro": Decimal("24500.00"),
            "Dell XPS 15": Decimal("185000.00"),
            "Sony WH-1000XM5": Decimal("38000.00"),
            "Office Ergonomic Chair": Decimal("16500.00"),
            "Smart LED Desk Lamp": Decimal("3200.00"),
            "Logitech MX Master 3S": Decimal("11500.00"),
            "Samsung 4K Monitor 27\"": Decimal("34000.00"),
        }

        # Weighted product popularity
        prod_weights = {
            "iPhone 15": 25,
            "ThinkPad X1 Carbon": 15,
            "Galaxy Tab S9": 14,
            "AirPods Pro": 20,
            "Dell XPS 15": 8,
            "Sony WH-1000XM5": 12,
            "Office Ergonomic Chair": 10,
            "Smart LED Desk Lamp": 18,
            "Logitech MX Master 3S": 22,
            "Samsung 4K Monitor 27\"": 10,
        }

        # Region weights: Dhaka (40%), Khulna (30%), Chittagong (20%), Sylhet (5%), Rajshahi (5%)
        reg_weights = [40, 20, 30, 5, 5]

        # Generate smooth monthly progression showing steady growth
        months_sales_volume = [
            (2026, 1, 28),
            (2026, 2, 32),
            (2026, 3, 38),
            (2026, 4, 42),
            (2026, 5, 48),
            (2026, 6, 55),
            (2026, 7, 62),
            (2026, 8, 40),  # Partial August
        ]

        for year, month, count in months_sales_volume:
            for _ in range(count):
                day = random.randint(1, 28)
                s_date = date(year, month, day)

                # Pick user (admin or managers)
                u = random.choice(users[:3])
                # Pick product
                prod = random.choices(products, weights=[prod_weights[p.name] for p in products])[0]
                # Pick region
                reg = random.choices(regions, weights=reg_weights)[0]

                # Quantity: 1-5 for high-ticket, 2-10 for low-ticket
                if prod.category in ["Phone", "Laptop"]:
                    qty = random.randint(1, 4)
                elif prod.category in ["Audio", "Electronics"]:
                    qty = random.randint(2, 6)
                else:
                    qty = random.randint(1, 5)

                unit_p = prices[prod.name]
                total_p = Decimal(qty) * unit_p

                # ~7% of historical rows simulate legacy date-only records with no captured
                # time-of-day, so the data-quality panel has something real to report.
                is_estimated = random.random() < 0.07
                if is_estimated:
                    sale_dt = datetime(s_date.year, s_date.month, s_date.day, 12, 0, 0, tzinfo=DHAKA_TZ)
                else:
                    hour = random.choices(list(HOUR_WEIGHTS.keys()), weights=list(HOUR_WEIGHTS.values()))[0]
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    sale_dt = datetime(s_date.year, s_date.month, s_date.day, hour, minute, second, tzinfo=DHAKA_TZ)

                sale = Sale(
                    user_id=u.id,
                    product_id=prod.id,
                    region_id=reg.id,
                    quantity=qty,
                    unit_price=unit_p,
                    total_price=total_p,
                    sale_date=s_date,
                    sale_datetime=sale_dt,
                    is_estimated_time=is_estimated,
                    created_at=datetime.combine(s_date, datetime.min.time()) + timedelta(hours=random.randint(9, 18))
                )
                sales_records.append(sale)

        db.bulk_save_objects(sales_records)
        db.commit()

        # 6. Seed Initial Notifications
        print("Seeding initial notifications...")
        notifs = [
            Notification(
                user_id=users[0].id,
                message="Low Stock Alert: Galaxy Tab S9 is down to 16 units across warehouses.",
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Notification(
                user_id=users[0].id,
                message="Sales Milestone: Total revenue surpassed ৳18,00,000 this quarter!",
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=6)
            ),
            Notification(
                user_id=users[1].id,
                message="Anomaly Flag: Sudden surge in iPhone 15 sales in Dhaka region.",
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=12)
            ),
            Notification(
                user_id=users[2].id,
                message="New monthly intelligence report is ready for export.",
                is_read=True,
                created_at=datetime.utcnow() - timedelta(days=1)
            ),
        ]
        db.add_all(notifs)
        db.commit()

        print("Seeding completed successfully!")
        print(f"-> {len(users)} users created")
        print(f"-> {len(regions)} regions created")
        print(f"-> {len(products)} products created")
        print(f"-> {len(sales_records)} sales records seeded spanning Jan-Aug 2026")
        print(f"-> {len(notifs)} notifications created")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
