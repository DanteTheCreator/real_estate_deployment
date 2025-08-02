#!/usr/bin/env python3
"""
Script to populate empty property addresses with meaningful dummy data
based on existing location information (city, district, urban_area).
"""

import psycopg2
import random
import sys
from typing import Dict, List

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'comfyrent_production',
    'user': 'comfyrent_user',
    'password': 'your_postgres_password'  # Will be read from secrets
}

# Georgian street patterns for different areas
STREET_PATTERNS = {
    # Tbilisi patterns
    'თბილისი': {
        'საბურთალო': [
            'კოსტავას ქ. {}', 'ღუდუშაურის ქ. {}', 'ვაჟა-ფშაველას ქ. {}', 
            'საბურთალოს ქ. {}', 'პეკინის ქ. {}', 'გ. ცაბაძის ქ. {}'
        ],
        'დიდი დიღომი': [
            'წავლის ქ. {}', 'სვანიძის ქ. {}', 'მიციშვილის ქ. {}',
            'ალ. ყაზბეგის ქ. {}', 'ალ. გრიბოედოვის ქ. {}'
        ],
        'ვაკე': [
            'ჭავჭავაძის ქ. {}', 'წერეთლის ქ. {}', 'აბაშიძის ქ. {}',
            'ბარნოვის ქ. {}', 'ვაჟა-ფშაველას ქ. {}', 'ლორთქიფანიძის ქ. {}'
        ],
        'ჩუღურეთი': [
            'წინანდლის ქ. {}', 'ზღვის ქ. {}', 'ერისთავი-ხოშტარიას ქ. {}',
            'ნინშოვას ქ. {}', 'ღუდუშაურის ქ. {}'
        ],
        'გლდანი': [
            'ახმეტელის ქ. {}', 'ნიაღვრის ქ. {}', 'წყაროს ქ. {}',
            'ბალანჩინეს ქ. {}', 'ტბილისის ზღვის ქ. {}'
        ],
        'ვარკეთილი': [
            'მუშის ქ. {}', 'ცისფერკანცელეობის ქ. {}', 'ნუცუბიძის ქ. {}',
            'თბილისის ქ. {}', 'მოსკოვის ქ. {}'
        ],
        'დიდუბე': [
            'ერისთავის ქ. {}', 'იაკობ გოგებაშვილის ქ. {}', 'დავით აღმაშენებლის ქ. {}',
            'კოტე აფხაზის ქ. {}', 'გია ჩანტურიას ქ. {}'
        ],
        'ვერა': [
            'ბარნოვის ქ. {}', 'ინგოროყვას ქ. {}', 'თავისუფლების ქ. {}',
            'რუსთაველის ქ. {}', 'ბაგრატიონის ქ. {}'
        ]
    },
    # Batumi patterns
    'ბათუმი': {
        'ხიმშიაშვილის უბანი': [
            'ხიმშიაშვილის ქ. {}', 'ყაზბეგის ქ. {}', 'მსახიობთა ქ. {}',
            'ვახუშტი ბაგრატიონის ქ. {}', 'მედეას ქ. {}'
        ],
        'აეროპორტის უბანი': [
            'აეროპორტის ქ. {}', 'ყველი ქ. {}', 'ბათუმის ქ. {}',
            'სამისი ქ. {}', 'ანტონოვის ქ. {}'
        ]
    }
}

def read_postgres_password():
    """Read postgres password from secrets file."""
    try:
        with open('/root/real_estate_deployment/secrets/postgres_password.txt', 'r') as f:
            return f.read().strip()
    except:
        return 'defaultpassword'  # fallback

def generate_address(city: str, urban_area: str) -> str:
    """Generate a realistic Georgian address based on location."""
    
    # Get street patterns for the city and area
    city_patterns = STREET_PATTERNS.get(city, {})
    area_patterns = city_patterns.get(urban_area, [])
    
    # If no specific patterns, use generic patterns
    if not area_patterns:
        # Generic patterns for any Georgian area
        area_patterns = [
            f'{urban_area} ქ. {{}}', 'რუსთაველის ქ. {}', 'თავისუფლების ქ. {}',
            'დავით აღმაშენებლის ქ. {}', 'ბაგრატიონის ქ. {}'
        ]
    
    # Choose random street pattern and building number
    street_pattern = random.choice(area_patterns)
    building_number = random.randint(1, 150)
    
    # Sometimes add apartment number for apartment buildings
    if random.random() < 0.3:  # 30% chance of apartment number
        apartment_number = random.randint(1, 50)
        return street_pattern.format(f"{building_number}, ბ. {apartment_number}")
    else:
        return street_pattern.format(str(building_number))

def update_empty_addresses():
    """Update all empty addresses in the database."""
    
    # Read password
    password = read_postgres_password()
    DB_CONFIG['password'] = password
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all properties with empty addresses
        cursor.execute("""
            SELECT id, city, state, district, urban_area 
            FROM properties 
            WHERE address IS NULL OR address = ''
            ORDER BY id
        """)
        
        empty_properties = cursor.fetchall()
        
        print(f"Found {len(empty_properties)} properties with empty addresses")
        
        updated_count = 0
        
        for prop_id, city, state, district, urban_area in empty_properties:
            # Generate address
            new_address = generate_address(city or 'თბილისი', urban_area or district or 'ცენტრი')
            
            # Update the property
            cursor.execute("""
                UPDATE properties 
                SET address = %s
                WHERE id = %s
            """, (new_address, prop_id))
            
            updated_count += 1
            
            if updated_count % 100 == 0:
                print(f"Updated {updated_count} addresses...")
                conn.commit()  # Commit in batches
        
        # Final commit
        conn.commit()
        print(f"✅ Successfully updated {updated_count} empty addresses")
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM properties WHERE address IS NULL OR address = ''")
        remaining_empty = cursor.fetchone()[0]
        print(f"Remaining empty addresses: {remaining_empty}")
        
    except Exception as e:
        print(f"❌ Error updating addresses: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    update_empty_addresses()
