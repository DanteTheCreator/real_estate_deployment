import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { ListingGrid } from '@/components/ListingGrid';
import { useProperties } from '@/hooks/useProperties';
import { useLanguage } from '@/contexts/LanguageContext';
import { SearchFilters } from '@/types';
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

  // Load initial properties when component mounts
  useEffect(() => {
    if (!hasSearched) {
      // Initial load - show all available properties with default pagination
      const defaultFilters: SearchFilters = {
        // Start with no filters to show all available properties
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
    <AppLayout showBanner={true} showSearch={true} onSearch={handleSearch}>
      <div className="py-8">
        <div className="container mx-auto px-4">
          {/* Results Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-bold text-foreground">
                {t('listings.availableProperties')}
              </h2>
              {totalCount > 0 && (
                <p className="text-sm text-muted-foreground mt-1">
                  {totalCount === 1 
                    ? `1 property found` 
                    : `${totalCount.toLocaleString()} properties available`
                  }
                  {totalPages > 1 && (
                    <span className="ml-2">
                      • Page {currentPage} of {totalPages}
                    </span>
                  )}
                </p>
              )}
              {!hasSearched && (
                <p className="text-sm text-muted-foreground mt-1">
                  Loading properties...
                </p>
              )}
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
                  
                  {/* Pagination Info */}
                  <div className="text-center text-sm text-muted-foreground mb-4">
                    Showing {((currentPage - 1) * 20) + 1} to {Math.min(currentPage * 20, totalCount)} of {totalCount.toLocaleString()} properties
                  </div>
                  
                  {/* Load More Button - Alternative to pagination for mobile */}
                  {currentPage < totalPages && (
                    <div className="text-center mb-6">
                      <button
                        onClick={() => goToPage(currentPage + 1)}
                        disabled={isLoading}
                        className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoading ? 'Loading...' : 'Load More Properties'}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* No Results */}
          {!isLoading && !error && properties.length === 0 && hasSearched && (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg">{t('listings.noProperties')}</p>
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
                Show All Properties
              </button>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default Index;