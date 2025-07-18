import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { ListingGrid } from '@/components/ListingGrid';
import { AdvancedSearchPanel } from '@/components/AdvancedSearchPanel';
import { useProperties } from '@/hooks/useProperties';
import { SearchFilters } from '@/types';
import { Loader2 } from 'lucide-react';

const Listings: React.FC = () => {
  const { searchProperties, properties, isLoading, error, totalCount } = useProperties();
  const [hasSearched, setHasSearched] = useState(false);

  // Load properties when component mounts or when search is triggered
  useEffect(() => {
    if (!hasSearched) {
      // Initial load - show all properties
      const defaultFilters: SearchFilters = {
        property_type: 'apartment'
      };
      searchProperties(defaultFilters);
      setHasSearched(true);
    }
  }, [hasSearched, searchProperties]);

  const handleSearch = async (filters: SearchFilters) => {
    await searchProperties(filters);
    setHasSearched(true);
  };

  return (
    <AppLayout showSearch={false}>
      <div className="py-8">
        {/* Advanced Search Panel */}
        <div className="mb-8">
          <AdvancedSearchPanel onSearch={handleSearch} />
        </div>

        {/* Results Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-foreground">Property Listings</h1>
          <div className="text-sm text-muted-foreground">
            {totalCount > 0 ? `${totalCount} properties found` : ''}
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin" />
            <span className="ml-2">Searching properties...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-12">
            <p className="text-red-600 mb-4">Error: {error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        )}

        {/* Results */}
        {!isLoading && !error && (
          <ListingGrid properties={properties} />
        )}
      </div>
    </AppLayout>
  );
};

export default Listings;