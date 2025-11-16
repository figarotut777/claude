-- Initialize database schema for Price-Scanner

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    image_url VARCHAR(1000),
    category VARCHAR(200),
    brand VARCHAR(200),
    normalized_name VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Marketplace listings
CREATE TABLE IF NOT EXISTS marketplace_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    marketplace VARCHAR(50) NOT NULL,
    marketplace_product_id VARCHAR(200),
    url VARCHAR(1000) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    rating DECIMAL(3, 2),
    reviews_count INTEGER,
    in_stock BOOLEAN DEFAULT true,
    seller_name VARCHAR(200),
    shipping_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(marketplace, marketplace_product_id)
);

-- Price history for tracking
CREATE TABLE IF NOT EXISTS price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES marketplace_listings(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User search history
CREATE TABLE IF NOT EXISTS search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    search_type VARCHAR(20) NOT NULL CHECK (search_type IN ('image', 'text', 'url')),
    query_data JSONB NOT NULL,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table (for future authentication)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(200),
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    api_key VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User watchlist
CREATE TABLE IF NOT EXISTS watchlist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    target_price DECIMAL(10, 2),
    notify_on_price_drop BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_normalized_name ON products(normalized_name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_product_id ON marketplace_listings(product_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_marketplace ON marketplace_listings(marketplace);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_price ON marketplace_listings(price);
CREATE INDEX IF NOT EXISTS idx_price_history_listing_id ON price_history(listing_id);
CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at);
CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist(user_id);

-- Full text search index
CREATE INDEX IF NOT EXISTS idx_products_name_fts ON products USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_products_description_fts ON products USING gin(to_tsvector('english', description));

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marketplace_listings_updated_at BEFORE UPDATE ON marketplace_listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
