-- Update empty addresses with meaningful dummy addresses based on location data
-- This will generate realistic Georgian addresses for properties with empty addresses

UPDATE properties 
SET address = CASE 
    -- For Tbilisi properties, create addresses based on districts
    WHEN city = 'თბილისი' AND urban_area = 'გლდანი' THEN 
        CASE 
            WHEN id % 10 = 0 THEN 'გლდანის ქ. ' || (10 + (id % 50))
            WHEN id % 10 = 1 THEN 'ახმეტელის ქ. ' || (5 + (id % 30))
            WHEN id % 10 = 2 THEN 'წერეთლის ქ. ' || (12 + (id % 40))
            WHEN id % 10 = 3 THEN 'ჯავახიშვილის ქ. ' || (8 + (id % 35))
            WHEN id % 10 = 4 THEN 'პეკინის ქ. ' || (15 + (id % 45))
            WHEN id % 10 = 5 THEN 'ვარკეთილის ქ. ' || (20 + (id % 25))
            WHEN id % 10 = 6 THEN 'სანზონის ქ. ' || (3 + (id % 32))
            WHEN id % 10 = 7 THEN 'მუხიანის ქ. ' || (7 + (id % 28))
            WHEN id % 10 = 8 THEN 'ღუდუშაურის ქ. ' || (11 + (id % 38))
            ELSE 'თემურ მეფის ქ. ' || (6 + (id % 42))
        END
    
    WHEN city = 'თბილისი' AND urban_area = 'საბურთალო' THEN 
        CASE 
            WHEN id % 8 = 0 THEN 'ვაჟა-ფშაველას ქ. ' || (25 + (id % 60))
            WHEN id % 8 = 1 THEN 'პოლიტკოვსკაიას ქ. ' || (8 + (id % 35))
            WHEN id % 8 = 2 THEN 'ალექსიძის ქ. ' || (14 + (id % 40))
            WHEN id % 8 = 3 THEN 'ცაბაძის ქ. ' || (18 + (id % 30))
            WHEN id % 8 = 4 THEN 'ჯიქიას ქ. ' || (22 + (id % 25))
            WHEN id % 8 = 5 THEN 'ყიფშიძის ქ. ' || (12 + (id % 48))
            WHEN id % 8 = 6 THEN 'ჯავახაძის ქ. ' || (35 + (id % 55))
            ELSE 'გურამიშვილის ქ. ' || (16 + (id % 33))
        END
    
    WHEN city = 'თბილისი' AND urban_area = 'დიდი დიღომი' THEN 
        CASE 
            WHEN id % 6 = 0 THEN 'აღმაშენებლის ქ. ' || (45 + (id % 80))
            WHEN id % 6 = 1 THEN 'დიღომის ქ. ' || (12 + (id % 50))
            WHEN id % 6 = 2 THEN 'მირიან მეფის ქ. ' || (8 + (id % 60))
            WHEN id % 6 = 3 THEN 'ბაგრატიონის ქ. ' || (25 + (id % 45))
            WHEN id % 6 = 4 THEN 'ვახტანგ VI ქ. ' || (18 + (id % 35))
            ELSE 'გიორგი სააკაძის ქ. ' || (30 + (id % 40))
        END
    
    WHEN city = 'თბილისი' AND urban_area = 'ვერა' THEN 
        CASE 
            WHEN id % 7 = 0 THEN 'კოსტავას ქ. ' || (15 + (id % 70))
            WHEN id % 7 = 1 THEN 'ბარნოვის ქ. ' || (8 + (id % 45))
            WHEN id % 7 = 2 THEN 'მელიქიშვილის ქ. ' || (22 + (id % 35))
            WHEN id % 7 = 3 THEN 'იაშვილის ქ. ' || (12 + (id % 28))
            WHEN id % 7 = 4 THEN 'ინგოროყვას ქ. ' || (6 + (id % 52))
            WHEN id % 7 = 5 THEN 'ყიფიანის ქ. ' || (18 + (id % 38))
            ELSE 'გრიბოედოვის ქ. ' || (25 + (id % 42))
        END

    WHEN city = 'თბილისი' AND state = 'ვაკე-საბურთალო' THEN 
        CASE 
            WHEN id % 5 = 0 THEN 'ვაკის ქ. ' || (20 + (id % 65))
            WHEN id % 5 = 1 THEN 'ჭავჭავაძის ქ. ' || (35 + (id % 85))
            WHEN id % 5 = 2 THEN 'ნუცუბიძის ქ. ' || (15 + (id % 40))
            WHEN id % 5 = 3 THEN 'ტაბუკაშვილის ქ. ' || (8 + (id % 30))
            ELSE 'ვერცხლის ქ. ' || (12 + (id % 45))
        END

    -- For Batumi properties
    WHEN city = 'ბათუმი' THEN 
        CASE 
            WHEN id % 8 = 0 THEN 'ბარათაშვილის ქ. ' || (5 + (id % 45))
            WHEN id % 8 = 1 THEN 'აღმაშენებლის ქ. ' || (15 + (id % 60))
            WHEN id % 8 = 2 THEN 'რუსთაველის ქ. ' || (8 + (id % 35))
            WHEN id % 8 = 3 THEN 'ზღვისპირეთის ქ. ' || (22 + (id % 50))
            WHEN id % 8 = 4 THEN 'ტაბიძის ქ. ' || (12 + (id % 28))
            WHEN id % 8 = 5 THEN 'შერიფ ხიმშიაშვილის ქ. ' || (18 + (id % 40))
            WHEN id % 8 = 6 THEN 'გორგასლის ქ. ' || (25 + (id % 55))
            ELSE 'მედეას ქ. ' || (10 + (id % 32))
        END

    -- For other Georgian cities
    WHEN city = 'ქუთაისი' THEN 
        CASE 
            WHEN id % 6 = 0 THEN 'რუსთაველის ქ. ' || (10 + (id % 50))
            WHEN id % 6 = 1 THEN 'ცაბაძის ქ. ' || (15 + (id % 35))
            WHEN id % 6 = 2 THEN 'ტაბუკაშვილის ქ. ' || (8 + (id % 28))
            WHEN id % 6 = 3 THEN 'გელოვანის ქ. ' || (20 + (id % 45))
            WHEN id % 6 = 4 THEN 'ცხენისძირის ქ. ' || (12 + (id % 38))
            ELSE 'დავით აღმაშენებლის ქ. ' || (25 + (id % 42))
        END

    WHEN city = 'გარდაბანი' THEN 
        CASE 
            WHEN id % 4 = 0 THEN 'რუსთაველის ქ. ' || (5 + (id % 30))
            WHEN id % 4 = 1 THEN 'აღმაშენებლის ქ. ' || (8 + (id % 25))
            WHEN id % 4 = 2 THEN 'ცენტრალური ქ. ' || (12 + (id % 35))
            ELSE 'ბაგრატიონის ქ. ' || (15 + (id % 28))
        END

    -- Default fallback for any remaining properties
    ELSE 
        CASE 
            WHEN urban_area IS NOT NULL AND urban_area != '' THEN urban_area || ' ქ. ' || (10 + (id % 50))
            WHEN state IS NOT NULL AND state != '' THEN state || ' ქ. ' || (15 + (id % 40))
            ELSE city || ' ქ. ' || (20 + (id % 35))
        END
END
WHERE address IS NULL OR address = '';

-- Show summary of updated records
SELECT 
    'Address Update Summary' as action,
    COUNT(*) as updated_properties,
    MIN(id) as min_property_id,
    MAX(id) as max_property_id
FROM properties 
WHERE address IS NOT NULL AND address != '' AND address LIKE '%ქ.%';
