#!/bin/bash

# Monitor scraper status and property count

echo "=== ComfyRent Scraper Monitor ==="
echo "Date: $(date)"
echo ""

# Check scraper container status
echo "🔍 Scraper Container Status:"
docker compose ps scraper --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
echo ""

# Get property count from database
echo "📊 Database Statistics:"
docker compose exec -T postgres psql -U comfyrent_user -d comfyrent_production -c "
SELECT 
    COUNT(*) as total_properties,
    COUNT(CASE WHEN source = 'myhome.ge' THEN 1 END) as myhome_properties,
    COUNT(CASE WHEN created_at::date = CURRENT_DATE THEN 1 END) as new_today,
    COUNT(CASE WHEN last_scraped::date = CURRENT_DATE THEN 1 END) as updated_today
FROM properties;
"
echo ""

# Show recent scraper logs
echo "📝 Recent Scraper Activity (last 10 lines):"
docker compose logs scraper --tail=10 | tail -10

echo ""
echo "=== Monitor Complete ==="
