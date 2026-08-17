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
INSERT INTO products (id, name, category, description, stock) VALUES
(1, 'iPhone 15', 'Phone', 'Latest flagship smartphone with dynamic island', 45),
(2, 'ThinkPad X1 Carbon', 'Laptop', 'High-end carbon-fiber business laptop', 28),
(3, 'Galaxy Tab S9', 'Tablet', 'Dynamic AMOLED 120Hz display with S-Pen', 16),
(4, 'AirPods Pro', 'Audio', 'Active noise cancellation wireless earbuds', 80),
(5, 'Dell XPS 15', 'Laptop', 'Premium 4K OLED creator laptop', 12),
(6, 'Sony WH-1000XM5', 'Audio', 'Industry-leading wireless ANC headphones', 35),
(7, 'Office Ergonomic Chair', 'Furniture', 'Ergonomic mesh chair with lumbar support', 65),
(8, 'Smart LED Desk Lamp', 'Furniture', 'Multi-angle dimmable color-temp desk lamp', 120),
(9, 'Logitech MX Master 3S', 'Electronics', 'High precision quiet-click wireless mouse', 90),
(10, 'Samsung 4K Monitor 27"', 'Electronics', 'Ultra HD IPS professional monitor', 25)
ON CONFLICT (id) DO NOTHING;

-- Demo Users (bcrypt hashes for: admin123, manager123, viewer123)
INSERT INTO users (id, name, email, password_hash, role) VALUES
(1, 'Mohaimeen Islam Pial', 'pial@example.com', '$2b$12$KkQ1bU4qEre4QGk.Zq3nxeZc5kP/3eN2uK8Hk5B6v1UqA1m0Z5Dhe', 'admin'),
(2, 'Sk Mesbaul Arefin', 'mesbaul@example.com', '$2b$12$0Gv0hO4E1v.aZ7iU4.97je7w4S6e6Qn9l2FkL1yP4w.gZ6jU4rIme', 'manager'),
(3, 'Sumaiya Akter', 'sumaiya@example.com', '$2b$12$0Gv0hO4E1v.aZ7iU4.97je7w4S6e6Qn9l2FkL1yP4w.gZ6jU4rIme', 'manager'),
(4, 'Afia Maliha Priota', 'priota@example.com', '$2b$12$XyZ9vU1mQ2oP3rS4tU5ve6w7x8y9z0A1B2C3D4E5F6G7H8I9J0Kme', 'viewer')
ON CONFLICT (id) DO NOTHING;

-- Sample Sales
INSERT INTO sales (user_id, product_id, region_id, quantity, unit_price, total_price, sale_date) VALUES
(1, 1, 1, 4, 87500.00, 350000.00, '2026-05-14'),
(1, 3, 2, 2, 62000.00, 124000.00, '2026-05-13'),
(2, 2, 3, 1, 142000.00, 142000.00, '2026-05-13'),
(2, 4, 1, 6, 24500.00, 147000.00, '2026-05-12'),
(3, 5, 1, 2, 185000.00, 370000.00, '2026-06-01'),
(3, 6, 2, 5, 38000.00, 190000.00, '2026-06-03'),
(1, 7, 3, 3, 16500.00, 49500.00, '2026-06-05'),
(2, 8, 4, 15, 3200.00, 48000.00, '2026-06-08'),
(1, 9, 1, 10, 11500.00, 115000.00, '2026-06-10'),
(2, 10, 5, 4, 34000.00, 136000.00, '2026-06-12');
