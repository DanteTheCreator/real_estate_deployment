-- Fix USD conversion for all properties
-- Convert GEL amounts to USD by dividing by 2.71 (current exchange rate)

UPDATE properties 
SET rent_amount_usd = ROUND(rent_amount / 2.71, 2)
WHERE rent_amount_usd IS NULL OR rent_amount_usd = rent_amount;

-- Verify the conversion
SELECT 
    id,
    title,
    rent_amount as gel_amount,
    rent_amount_usd as usd_amount,
    ROUND(rent_amount / 2.71, 2) as calculated_usd
FROM properties 
WHERE rent_amount_usd IS NOT NULL
LIMIT 10;
