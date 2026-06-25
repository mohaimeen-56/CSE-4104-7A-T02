-- ============================================================
-- CSE4104-7A-T02 | AI Sales Analytics Dashboard
-- Database Schema for PostgreSQL (Supabase)
-- ============================================================

-- Drop tables if they already exist (useful for re-running during development)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS ai_logs CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS regions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================
-- TABLE: users
-- ============================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'manager', 'viewer')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: products
-- ============================================================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    stock INT DEFAULT 0 CHECK (stock >= 0),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: regions
-- ============================================================
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'Bangladesh',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: sales
-- ============================================================
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    region_id INT NOT NULL REFERENCES regions(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    total_price NUMERIC(12,2) NOT NULL CHECK (total_price >= 0),
    sale_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: ai_logs
-- ============================================================
CREATE TABLE ai_logs (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: notifications
-- ============================================================
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INDEXES — improve query performance for common filters
-- ============================================================
CREATE INDEX idx_sales_user_id ON sales(user_id);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_sales_region_id ON sales(region_id);
CREATE INDEX idx_sales_sale_date ON sales(sale_date);
CREATE INDEX idx_ai_logs_user_id ON ai_logs(user_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- ============================================================
-- SEED DATA — sample data for development/testing
-- ============================================================

-- Sample regions
INSERT INTO regions (name, country) VALUES
('Dhaka', 'Bangladesh'),
('Chittagong', 'Bangladesh'),
('Khulna', 'Bangladesh'),
('Sylhet', 'Bangladesh'),
('Rajshahi', 'Bangladesh');

-- Sample products
INSERT INTO products (name, category, description, stock) VALUES
('Laptop', 'Electronics', 'High performance laptop', 50),
('Smartphone', 'Electronics', 'Latest model smartphone', 120),
('Office Chair', 'Furniture', 'Ergonomic office chair', 75),
('Desk Lamp', 'Furniture', 'LED desk lamp', 200),
('Wireless Mouse', 'Electronics', 'Bluetooth wireless mouse', 300);

-- Sample admin user (password should be bcrypt-hashed in real app, this is a placeholder hash)
INSERT INTO users (name, email, password_hash, role) VALUES
('Mohaimeen Islam Pial', 'pial@example.com', '$2b$12$placeholderhashvalueforadminuser1234567890', 'admin'),
('Sk Mesbaul Arefin', 'mesbaul@example.com', '$2b$12$placeholderhashvalueformanageruser123456', 'manager'),
('Sumaiya Akter', 'sumaiya@example.com', '$2b$12$placeholderhashvalueformanageruser654321', 'manager'),
('Afia Maliha Priota', 'priota@example.com', '$2b$12$placeholderhashvalueforvieweruser1234567', 'viewer');

-- Sample sales records
INSERT INTO sales (user_id, product_id, region_id, quantity, unit_price, total_price, sale_date) VALUES
(1, 1, 1, 5, 45000.00, 225000.00, '2026-06-01'),
(1, 2, 1, 10, 25000.00, 250000.00, '2026-06-03'),
(2, 3, 2, 3, 8000.00, 24000.00, '2026-06-05'),
(2, 1, 3, 2, 45000.00, 90000.00, '2026-06-07'),
(3, 4, 1, 15, 1200.00, 18000.00, '2026-06-10'),
(3, 5, 2, 20, 800.00, 16000.00, '2026-06-12'),
(1, 2, 4, 8, 25000.00, 200000.00, '2026-06-15'),
(2, 1, 1, 4, 45000.00, 180000.00, '2026-06-18');

-- ============================================================
-- END OF SCHEMA
-- ============================================================
