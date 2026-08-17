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
-- Note: user_id is nullable so historical sales records persist
-- if a user is deleted (ON DELETE SET NULL).
-- ============================================================
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
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
