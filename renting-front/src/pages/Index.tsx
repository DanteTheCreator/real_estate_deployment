import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { ListingGrid } from '@/components/ListingGrid';
import { SortComponent } from '@/components/SortComponent';
import { useProperties } from '@/hooks/useProperties';
import { useLanguage } from '@/contexts/LanguageContext';
import { SearchFilters } from '@/types';
import { propertyService } from '@/services';
import { Loader2 } from 'lucide-react';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const Index: React.FC = () => {
  const { searchProperties, properties, isLoading, error, totalCount, currentPage, totalPages, goToPage } = useProperties();
  const { t } = useLanguage();
  const [hasSearched, setHasSearched] = useState(false);
  const [totalAvailableProperties, setTotalAvailableProperties] = useState<number | null>(null);
  const [currentSortBy, setCurrentSortBy] = useState('date');
  const [currentSortOrder, setCurrentSortOrder] = useState('desc');
  const [currentFilters, setCurrentFilters] = useState<SearchFilters>({});

  // Load total available properties count
  useEffect(() => {
    const loadTotalCount = async () => {
      try {
        const response = await propertyService.getTotalPropertiesCount();
        setTotalAvailableProperties(response.total_count);
      } catch (error) {
        console.error('Failed to load total properties count:', error);
      }
    };
    
    loadTotalCount();
  }, []);

  // Load initial properties when component mounts
  useEffect(() => {
    if (!hasSearched) {
      // Initial load - show all available properties with default sorting
      const defaultFilters: SearchFilters = {
        sort_by: currentSortBy as 'price' | 'area' | 'date' | 'bedrooms',
        sort_order: currentSortOrder as 'asc' | 'desc'
      };
      setCurrentFilters(defaultFilters);
      searchProperties(defaultFilters);
      setHasSearched(true);
    }
  }, [hasSearched, searchProperties, currentSortBy, currentSortOrder]);

  const handleSearch = async (filters: SearchFilters) => {
    // Add current sort parameters to the search filters
    const filtersWithSort = {
      ...filters,
      sort_by: currentSortBy as 'price' | 'area' | 'date' | 'bedrooms',
      sort_order: currentSortOrder as 'asc' | 'desc'
    };
    
    setCurrentFilters(filtersWithSort);
    await searchProperties(filtersWithSort);
    setHasSearched(true);
  };

  const handleSortChange = async (sortBy: string, sortOrder: string) => {
    setCurrentSortBy(sortBy);
    setCurrentSortOrder(sortOrder);
    
    // Apply sort to current search results
    const updatedFilters = {
      ...currentFilters,
      sort_by: sortBy as 'price' | 'area' | 'date' | 'bedrooms',
      sort_order: sortOrder as 'asc' | 'desc'
    };
    
    setCurrentFilters(updatedFilters);
    await searchProperties(updatedFilters);
  };

  return (
    <AppLayout showBanner={true} showSearch={true} onSearch={handleSearch}>
      <div className="py-8">
        <div className="container mx-auto px-4">
          {/* Results Header with Sort */}
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                Discover Your Perfect Home
              </h1>
              {totalAvailableProperties !== null && (
                <p className="text-sm text-muted-foreground">
                  Explore {totalAvailableProperties.toLocaleString()} unique properties
                </p>
              )}
              {!hasSearched && (
                <p className="text-sm text-muted-foreground mt-1">
                  Loading properties...
                </p>
              )}
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              {/* Quick Sort Controls - Show always when search has been performed */}
              {(properties.length > 0 || hasSearched) && (
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-muted-foreground">Sort by:</span>
                  <SortComponent
                    sortBy={currentSortBy}
                    sortOrder={currentSortOrder}
                    onSortChange={handleSortChange}
                    compact={true}
                  />
                </div>
              )}
              
              {/* Results Count */}
              <div className="text-right">
                {totalCount > 0 && (
                  <p className="text-sm text-muted-foreground">
                    {totalCount === 1 
                      ? `1 property found` 
                      : `${totalCount.toLocaleString()} search results`
                    }
                  </p>
                )}
                {totalPages > 1 && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Page {currentPage} of {totalPages}
                  </p>
                )}
              </div>
            </div>
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
            <>
              <ListingGrid properties={properties} />
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex flex-col items-center space-y-4">
                  <Pagination>
                    <PaginationContent>
                      <PaginationItem>
                        <PaginationPrevious 
                          href="#"
                          onClick={(e) => {
                            e.preventDefault();
                            if (currentPage > 1) {
                              goToPage(currentPage - 1);
                            }
                          }}
                          className={currentPage <= 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                        />
                      </PaginationItem>
                      
                      {[...Array(Math.min(totalPages, 5))].map((_, idx) => {
                        let pageNumber;
                        if (totalPages <= 5) {
                          pageNumber = idx + 1;
                        } else if (currentPage <= 3) {
                          pageNumber = idx + 1;
                        } else if (currentPage >= totalPages - 2) {
                          pageNumber = totalPages - 4 + idx;
                        } else {
                          pageNumber = currentPage - 2 + idx;
                        }
                        
                        return (
                          <PaginationItem key={pageNumber}>
                            <PaginationLink
                              href="#"
                              onClick={(e) => {
                                e.preventDefault();
                                goToPage(pageNumber);
                              }}
                              isActive={currentPage === pageNumber}
                              className="cursor-pointer"
                            >
                              {pageNumber}
                            </PaginationLink>
                          </PaginationItem>
                        );
                      })}
                      
                      {totalPages > 5 && currentPage < totalPages - 2 && (
                        <PaginationItem>
                          <PaginationEllipsis />
                        </PaginationItem>
                      )}
                      
                      <PaginationItem>
                        <PaginationNext 
                          href="#"
                          onClick={(e) => {
                            e.preventDefault();
                            if (currentPage < totalPages) {
                              goToPage(currentPage + 1);
                            }
                          }}
                          className={currentPage >= totalPages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                        />
                      </PaginationItem>
                    </PaginationContent>
                  </Pagination>
                </div>
              )}
            </>
          )}

          {/* No Results */}
          {!isLoading && !error && properties.length === 0 && hasSearched && (
            <div className="text-center py-12">
              <h3 className="text-xl font-semibold text-muted-foreground mb-2">
                No properties match your search
              </h3>
              <p className="text-muted-foreground text-lg mb-2">{t('listings.noProperties')}</p>
              <p className="text-sm text-muted-foreground mt-2 mb-6">
                {t('listings.adjustFilters')}
              </p>
              <button 
                onClick={() => {
                  const defaultFilters: SearchFilters = {};
                  handleSearch(defaultFilters);
                }}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
              >
                Browse All Properties
              </button>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default Index;