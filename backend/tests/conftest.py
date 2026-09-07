import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User
from app.models.product import Product
from app.models.region import Region
from app.models.sale import Sale
from app.core.security import get_password_hash, create_access_token

# Pre-hash once at module import
H_ADMIN = get_password_hash('admin123')
H_MANAGER = get_password_hash('manager123')
H_VIEWER = get_password_hash('viewer123')

@pytest.fixture(scope='function')
def db_session(tmp_path):
    db_file = tmp_path / 'test.db'
    engine = create_engine(f'sqlite:///{db_file}', connect_args={'check_same_thread': False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    admin = User(
        name='Admin User',
        email='admin@test.com',
        password_hash=H_ADMIN,
        role='admin',
    )
    manager = User(
        name='Manager User',
        email='manager@test.com',
        password_hash=H_MANAGER,
        role='manager',
    )
    viewer = User(
        name='Viewer User',
        email='viewer@test.com',
        password_hash=H_VIEWER,
        role='viewer',
    )
    db.add_all([admin, manager, viewer])
    db.commit()

    r_dhaka = Region(name='Dhaka', country='Bangladesh')
    r_khulna = Region(name='Khulna', country='Bangladesh')
    r_ctg = Region(name='Chittagong', country='Bangladesh')
    db.add_all([r_dhaka, r_khulna, r_ctg])
    db.commit()

    p1 = Product(name='Laptop Pro', category='Electronics', subcategory='Laptops', brand='TechBrand', price=1200.0, cost=900.0, stock=50)
    p2 = Product(name='Wireless Mouse', category='Electronics', subcategory='Accessories', brand='TechBrand', price=25.0, cost=12.0, stock=15)
    p3 = Product(name='Desk Chair', category='Furniture', subcategory='Chairs', brand='FurniCo', price=150.0, cost=80.0, stock=30)
    db.add_all([p1, p2, p3])
    db.commit()

    s1 = Sale(product_id=p1.id, region_id=r_dhaka.id, quantity=2, unit_price=1200.0, total_price=2400.0, sale_date=date(2026, 8, 10), sale_datetime=datetime(2026, 8, 10, 14, 30))
    s2 = Sale(product_id=p2.id, region_id=r_khulna.id, quantity=5, unit_price=25.0, total_price=125.0, sale_date=date(2026, 8, 15), sale_datetime=datetime(2026, 8, 15, 11, 0))
    s3 = Sale(product_id=p3.id, region_id=r_ctg.id, quantity=1, unit_price=150.0, total_price=150.0, sale_date=date(2026, 9, 1), sale_datetime=datetime(2026, 9, 1, 16, 45))
    db.add_all([s1, s2, s3])
    db.commit()

    try:
        yield db
    finally:
        db.close()
        engine.dispose()

@pytest.fixture(scope='function')
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_headers(db_session):
    user = db_session.query(User).filter(User.email == 'admin@test.com').first()
    token = create_access_token(subject=user.id, role='admin')
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def manager_headers(db_session):
    user = db_session.query(User).filter(User.email == 'manager@test.com').first()
    token = create_access_token(subject=user.id, role='manager')
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def viewer_headers(db_session):
    user = db_session.query(User).filter(User.email == 'viewer@test.com').first()
    token = create_access_token(subject=user.id, role='viewer')
    return {'Authorization': f'Bearer {token}'}
