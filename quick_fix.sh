#!/bin/bash

echo "🚀 Quick Performance Fix - Applying Database Indexes"
echo "=================================================="

# Apply database indexes directly using docker exec
echo "📊 Adding critical database indexes..."

# Run the optimization inside the postgres container
docker exec -i comfyrent-postgres psql -U comfyrent_user -d comfyrent_production << 'EOF'
-- Add critical indexes for immediate performance improvement
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_is_available ON properties (is_available);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_created_at ON properties (created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_city ON properties (city);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_rent_amount ON properties (rent_amount);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_available_date ON properties (is_available, created_at DESC) WHERE is_available = true;

-- Update table statistics
ANALYZE properties;

-- Show created indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'properties' AND indexname LIKE 'idx_properties_%';
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Critical indexes added successfully!"
    echo "📈 Your API should be faster immediately!"
else
    echo "❌ Failed to add indexes - database may not be ready"
fi
