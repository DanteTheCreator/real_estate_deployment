-- Complete database setup with proper CASCADE DELETE constraints
-- This creates all tables needed for the real estate scraper

-- 1. Users table (parent table)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Amenities table (parent table)
CREATE TABLE IF NOT EXISTS amenities (
    id SERIAL PRIMARY KEY,
    external_id INTEGER UNIQUE,
    key VARCHAR(100),
    sort_index INTEGER DEFAULT 0,
    amenity_type VARCHAR(50),
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Parameters table (parent table)
CREATE TABLE IF NOT EXISTS parameters (
    id SERIAL PRIMARY KEY,
    external_id INTEGER UNIQUE,
    key VARCHAR(100),
    sort_index INTEGER DEFAULT 0,
    parameter_type VARCHAR(50),
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Properties table (references users)
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(50) UNIQUE NOT NULL,
    source VARCHAR(50) DEFAULT 'myhome.ge',
    
    -- Basic info
    title TEXT,
    description TEXT,
    price DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'GEL',
    price_usd DECIMAL(12,2),
    
    -- Property details
    property_type INTEGER,
    deal_type INTEGER,
    area DECIMAL(8,2),
    room_count INTEGER,
    bedroom_count INTEGER,
    bathroom_count INTEGER,
    floor INTEGER,
    total_floors INTEGER,
    
    -- Location
    address TEXT,
    city VARCHAR(100),
    district VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    
    -- Multilingual content
    title_en TEXT,
    title_ka TEXT,
    title_ru TEXT,
    description_en TEXT,
    description_ka TEXT,
    description_ru TEXT,
    
    -- Status
    is_available BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'active',
    
    -- Relationships
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_external_source UNIQUE (external_id, source)
);

-- 5. Property Images (references properties with CASCADE DELETE)
CREATE TABLE IF NOT EXISTS property_images (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    external_id VARCHAR(50),
    image_url TEXT NOT NULL,
    local_path TEXT,
    image_type VARCHAR(20) DEFAULT 'photo',
    sort_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT false,
    width INTEGER,
    height INTEGER,
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Property Parameters (references properties and parameters with CASCADE DELETE)
CREATE TABLE IF NOT EXISTS property_parameters (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    parameter_id INTEGER NOT NULL REFERENCES parameters(id) ON DELETE CASCADE,
    value TEXT,
    value_type VARCHAR(20) DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_property_parameter UNIQUE (property_id, parameter_id)
);

-- 7. Property Prices (references properties with CASCADE DELETE)
CREATE TABLE IF NOT EXISTS property_prices (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GEL',
    price_usd DECIMAL(12,2),
    price_type VARCHAR(20) DEFAULT 'sale',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Property Amenities (references properties and amenities with CASCADE DELETE)
CREATE TABLE IF NOT EXISTS property_amenities (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    amenity_id INTEGER NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_property_amenity UNIQUE (property_id, amenity_id)
);

-- 9. Saved Properties (references users and properties with CASCADE DELETE)
CREATE TABLE IF NOT EXISTS saved_properties (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_saved_property UNIQUE (user_id, property_id)
);

-- 10. Rental Applications (references users and properties with CASCADE DELETE)
CREATE TABLE IF NOT EXISTS rental_applications (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    tenant_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_properties_external_id ON properties(external_id);
CREATE INDEX IF NOT EXISTS idx_properties_source ON properties(source);
CREATE INDEX IF NOT EXISTS idx_properties_owner_id ON properties(owner_id);
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type, deal_type);
CREATE INDEX IF NOT EXISTS idx_property_images_property_id ON property_images(property_id);
CREATE INDEX IF NOT EXISTS idx_property_parameters_property_id ON property_parameters(property_id);
CREATE INDEX IF NOT EXISTS idx_property_prices_property_id ON property_prices(property_id);

-- Insert default system user
INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified)
VALUES ('system@scraper.com', 'dummy_hash', 'System', 'Scraper', 'admin', true, true)
ON CONFLICT (email) DO NOTHING;

-- Insert basic parameters
INSERT INTO parameters (external_id, key, parameter_type, display_name) VALUES
(1, 'rooms', 'parameter', 'Rooms'),
(2, 'bathrooms', 'parameter', 'Bathrooms'),
(3, 'floor', 'parameter', 'Floor'),
(4, 'area', 'parameter', 'Area'),
(5, 'parking', 'parameter', 'Parking')
ON CONFLICT (external_id) DO NOTHING;

-- Insert basic amenities
INSERT INTO amenities (external_id, key, amenity_type, display_name) VALUES
(1, 'balcony', 'amenity', 'Balcony'),
(2, 'elevator', 'amenity', 'Elevator'),
(3, 'garage', 'amenity', 'Garage'),
(4, 'garden', 'amenity', 'Garden'),
(5, 'pool', 'amenity', 'Swimming Pool')
ON CONFLICT (external_id) DO NOTHING;
