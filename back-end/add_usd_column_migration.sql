-- Migration to add rent_amount_usd column to properties table
-- Run this SQL script to add the USD rent amount column

-- Add the new column
ALTER TABLE properties ADD COLUMN rent_amount_usd FLOAT;

-- Update existing records where we have USD price data
-- This will be populated automatically by the scraper for new records
UPDATE properties 
SET rent_amount_usd = rent_amount 
WHERE rent_amount_usd IS NULL 
  AND source = 'myhome.ge' 
  AND EXISTS (
    SELECT 1 FROM property_prices 
    WHERE property_prices.property_id = properties.id 
    AND property_prices.currency_type = '1'
  );

-- Add index for better query performance on USD amounts
CREATE INDEX IF NOT EXISTS idx_properties_rent_amount_usd ON properties(rent_amount_usd) WHERE rent_amount_usd IS NOT NULL;

-- Add comment to document the column
COMMENT ON COLUMN properties.rent_amount_usd IS 'Rent amount in USD currency specifically, separate from general rent_amount which may be in any currency';
