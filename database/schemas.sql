-- ============================================================
-- CSE4104-7A-T02 | AI Sales Analytics Dashboard
-- Complete Production Database Schema for PostgreSQL (Supabase)
-- ============================================================

-- Drop tables if they already exist in reverse dependency order
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS ai_logs CASCADE;
DROP TABLE IF EXISTS maintenance_logs CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS regions CASCADE;
DROP TABLE IF EXISTS admin_invite_codes CASCADE;
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
-- TABLE: admin_invite_codes
-- ============================================================
CREATE TABLE admin_invite_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    created_by_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    used BOOLEAN DEFAULT FALSE NOT NULL,
    used_by_id INT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

-- ============================================================
-- TABLE: products
-- ============================================================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    subcategory VARCHAR(50),
    brand VARCHAR(100),
    sku VARCHAR(50) UNIQUE,
    description TEXT,
    price NUMERIC(10,2),
    cost NUMERIC(10,2),
    stock INT DEFAULT 0 CHECK (stock >= 0),
    production_level VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
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
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    region_id INT NOT NULL REFERENCES regions(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    total_price NUMERIC(12,2) NOT NULL CHECK (total_price >= 0),
    sale_date DATE NOT NULL,
    sale_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    is_estimated_time BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: system_settings
-- ============================================================
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_by INT REFERENCES users(id) ON DELETE SET NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: maintenance_logs
-- ============================================================
CREATE TABLE maintenance_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(20) NOT NULL,
    performed_by INT REFERENCES users(id) ON DELETE SET NULL,
    reason TEXT,
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
-- INDEXES
-- ============================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_admin_invite_codes_code ON admin_invite_codes(code);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_sales_user_id ON sales(user_id);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_sales_region_id ON sales(region_id);
CREATE INDEX idx_sales_sale_date ON sales(sale_date);
CREATE INDEX idx_sales_sale_datetime ON sales(sale_datetime);
CREATE INDEX idx_system_settings_key ON system_settings(key);
CREATE INDEX idx_maintenance_logs_created_at ON maintenance_logs(created_at);
CREATE INDEX idx_ai_logs_user_id ON ai_logs(user_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
