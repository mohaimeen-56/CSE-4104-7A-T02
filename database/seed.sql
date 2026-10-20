-- ============================================================
-- CSE4104-7A-T02 | AI Sales Analytics Dashboard
-- Seed Data for PostgreSQL / Supabase
-- ============================================================

-- Regions
INSERT INTO regions (id, name, country) VALUES
(1, 'Dhaka', 'Bangladesh'),
(2, 'Chittagong', 'Bangladesh'),
(3, 'Khulna', 'Bangladesh'),
(4, 'Sylhet', 'Bangladesh'),
(5, 'Rajshahi', 'Bangladesh')
ON CONFLICT (id) DO NOTHING;

-- Products
INSERT INTO products (id, name, category, subcategory, brand, description, price, cost, stock, production_level, is_active) VALUES
(1, 'iPhone 15', 'Electronics', 'Phones', 'Apple', 'Latest flagship smartphone with dynamic island', 87500.00, 72000.00, 45, 'medium', true),
(2, 'ThinkPad X1 Carbon', 'Electronics', 'Laptops', 'Lenovo', 'High-end carbon-fiber business laptop', 142000.00, 115000.00, 28, 'medium', true),
(3, 'Galaxy Tab S9', 'Electronics', 'Tablets', 'Samsung', 'Dynamic AMOLED 120Hz display with S-Pen', 62000.00, 50000.00, 16, 'low', true),
(4, 'AirPods Pro', 'Electronics', 'Audio', 'Apple', 'Active noise cancellation wireless earbuds', 24500.00, 18000.00, 80, 'high', true),
(5, 'Dell XPS 15', 'Electronics', 'Laptops', 'Dell', 'Premium 4K OLED creator laptop', 185000.00, 150000.00, 12, 'low', true),
(6, 'Sony WH-1000XM5', 'Electronics', 'Audio', 'Sony', 'Industry-leading wireless ANC headphones', 38000.00, 30000.00, 35, 'medium', true),
(7, 'Office Ergonomic Chair', 'Furniture', 'Chairs', 'ErgoComfort', 'Ergonomic mesh chair with lumbar support', 16500.00, 12000.00, 65, 'high', true),
(8, 'Smart LED Desk Lamp', 'Furniture', 'Lighting', 'Lumina', 'Multi-angle dimmable color-temp desk lamp', 3200.00, 2100.00, 120, 'high', true),
(9, 'Logitech MX Master 3S', 'Electronics', 'Accessories', 'Logitech', 'High precision quiet-click wireless mouse', 11500.00, 8500.00, 90, 'high', true),
(10, 'Samsung 4K Monitor 27"', 'Electronics', 'Displays', 'Samsung', 'Ultra HD IPS professional monitor', 34000.00, 26000.00, 25, 'medium', true)
ON CONFLICT (id) DO NOTHING;

-- Demo Users (passwords: admin123, manager123, viewer123)
INSERT INTO users (id, name, email, password_hash, role) VALUES
(1, 'Mohaimeen Islam Pial', 'pial@example.com', '$2b$12$KkQ1bU4qEre4QGk.Zq3nxeZc5kP/3eN2uK8Hk5B6v1UqA1m0Z5Dhe', 'admin'),
(2, 'Sk Mesbaul Arefin', 'mesbaul@example.com', '$2b$12$0Gv0hO4E1v.aZ7iU4.97je7w4S6e6Qn9l2FkL1yP4w.gZ6jU4rIme', 'manager'),
(3, 'Sumaiya Akter', 'sumaiya@example.com', '$2b$12$0Gv0hO4E1v.aZ7iU4.97je7w4S6e6Qn9l2FkL1yP4w.gZ6jU4rIme', 'manager'),
(4, 'Afia Maliha Priota', 'priota@example.com', '$2b$12$XyZ9vU1mQ2oP3rS4tU5ve6w7x8y9z0A1B2C3D4E5F6G7H8I9J0Kme', 'viewer')
ON CONFLICT (id) DO NOTHING;

-- Sample Sales
INSERT INTO sales (id, user_id, product_id, region_id, quantity, unit_price, total_price, sale_date, sale_datetime, is_estimated_time) VALUES
(1, 1, 1, 1, 4, 87500.00, 350000.00, '2026-05-14', '2026-05-14 10:30:00+00', false),
(2, 1, 3, 2, 2, 62000.00, 124000.00, '2026-05-13', '2026-05-13 14:15:00+00', false),
(3, 2, 2, 3, 1, 142000.00, 142000.00, '2026-05-13', '2026-05-13 11:00:00+00', false),
(4, 2, 4, 1, 6, 24500.00, 147000.00, '2026-05-12', '2026-05-12 16:45:00+00', false),
(5, 3, 5, 1, 2, 185000.00, 370000.00, '2026-06-01', '2026-06-01 09:30:00+00', false),
(6, 3, 6, 2, 5, 38000.00, 190000.00, '2026-06-03', '2026-06-03 15:00:00+00', false),
(7, 1, 7, 3, 3, 16500.00, 49500.00, '2026-06-05', '2026-06-05 13:20:00+00', false),
(8, 2, 8, 4, 15, 3200.00, 48000.00, '2026-06-08', '2026-06-08 17:10:00+00', false),
(9, 1, 9, 1, 10, 11500.00, 115000.00, '2026-06-10', '2026-06-10 12:00:00+00', false),
(10, 2, 10, 5, 4, 34000.00, 136000.00, '2026-06-12', '2026-06-12 18:30:00+00', false)
ON CONFLICT (id) DO NOTHING;

-- Reset serial sequences to avoid duplicate key conflicts on subsequent inserts
SELECT setval('regions_id_seq', (SELECT COALESCE(MAX(id), 1) FROM regions));
SELECT setval('products_id_seq', (SELECT COALESCE(MAX(id), 1) FROM products));
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));
SELECT setval('sales_id_seq', (SELECT COALESCE(MAX(id), 1) FROM sales));
