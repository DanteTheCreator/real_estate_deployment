import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { ListingGrid } from '@/components/ListingGrid';
import { useProperties } from '@/hooks/useProperties';
import { useLanguage } from '@/contexts/LanguageContext';
import { SearchFilters } from '@/types';
import { Loader2 } from 'lucide-react';

const Index: React.FC = () => {
  const { searchProperties, properties, isLoading, error, totalCount } = useProperties();
  const { t } = useLanguage();
  const [hasSearched, setHasSearched] = useState(false);

  // Load initial properties when component mounts
  useEffect(() => {
    if (!hasSearched) {
      // Initial load - show all properties
      const defaultFilters: SearchFilters = {};
      searchProperties(defaultFilters);
      setHasSearched(true);
    }
  }, [hasSearched, searchProperties]);

  const handleSearch = async (filters: SearchFilters) => {
    await searchProperties(filters);
    setHasSearched(true);
  };

  return (
    <AppLayout showBanner={true} showSearch={true} onSearch={handleSearch}>
      <div className="py-8">
        <div className="container mx-auto px-4">
          {/* Results Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-foreground">
              {totalCount > 0 ? `${t('listings.availableProperties')} (${totalCount})` : t('listings.availableProperties')}
            </h2>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">{t('common.loading')}</span>
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <div className="text-center py-12">
              <p className="text-red-600 mb-4">{t('common.error')}: {error}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Retry
              </button>
            </div>
          )}

          {/* Results */}
          {!isLoading && !error && properties.length > 0 && (
            <ListingGrid properties={properties} />
          )}

          {/* No Results */}
          {!isLoading && !error && properties.length === 0 && hasSearched && (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg">{t('listings.noProperties')}</p>
              <p className="text-sm text-muted-foreground mt-2">
                {t('listings.adjustFilters')}
              </p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default Index;