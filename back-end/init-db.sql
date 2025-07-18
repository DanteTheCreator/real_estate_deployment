-- Initialize the real-estate-rental database
-- This script runs when the PostgreSQL container starts for the first time

-- Create the database (this might already be created by POSTGRES_DB env var)
-- SELECT 'CREATE DATABASE "real-estate-rental"' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'real-estate-rental')\gexec

-- Connect to the database
\c real-estate-rental;

-- Create any additional extensions if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The actual tables will be created by SQLAlchemy when the application starts
-- This file is mainly for any initial setup that needs to happen at the database level

-- Grant necessary permissions to the user
GRANT ALL PRIVILEGES ON DATABASE "real-estate-rental" TO "real-estate-user";
