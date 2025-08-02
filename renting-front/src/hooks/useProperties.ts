import { useState, useEffect, useCallback } from 'react';
import { Property, SearchFilters, UsePropertiesReturn, UsePropertyReturn, UseFavoritesReturn } from '@/types';
import { propertyService, userService } from '@/services';
import { useAppContext } from '@/contexts/AppContext';
import { useCurrency } from '@/contexts/CurrencyContext';

export const useProperties = (): UsePropertiesReturn => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentFilters, setCurrentFilters] = useState<SearchFilters | null>(null);

  const { addRecentSearch } = useAppContext();
  const { currency } = useCurrency();

  // Convert price filters based on current currency
  const convertPriceFilters = useCallback((filters: SearchFilters): SearchFilters => {
    const convertedFilters = { ...filters };
    
    // If user is searching in USD but backend expects GEL, convert the price ranges
    if (currency === 'USD') {
      // Convert USD price filters to GEL for backend filtering
      if (convertedFilters.min_rent !== undefined) {
        convertedFilters.min_rent = convertedFilters.min_rent * 2.71; // Convert USD to GEL
      }
      if (convertedFilters.max_rent !== undefined) {
        convertedFilters.max_rent = convertedFilters.max_rent * 2.71; // Convert USD to GEL
      }
      // Also handle legacy price fields
      if (convertedFilters.priceMin !== undefined) {
        convertedFilters.priceMin = convertedFilters.priceMin * 2.71;
      }
      if (convertedFilters.priceMax !== undefined) {
        convertedFilters.priceMax = convertedFilters.priceMax * 2.71;
      }
    }
    
    return convertedFilters;
  }, [currency]);

  const searchProperties = useCallback(async (filters: SearchFilters, resetPage = true) => {
    setIsLoading(true);
    setError(null);
    
    // Convert price filters based on current currency
    const convertedFilters = convertPriceFilters(filters);
    setCurrentFilters(convertedFilters);

    try {
      const pageToUse = resetPage ? 1 : currentPage;
      const response = await propertyService.searchProperties(convertedFilters, pageToUse, 20);
      
      console.log('useProperties.searchProperties response:', response);
      
      if (resetPage) {
        setProperties(response.data);
        setCurrentPage(1);
      } else {
        setProperties(response.data);
        setCurrentPage(response.pagination.currentPage);
      }
      
      setTotalCount(response.pagination.totalCount);
      setTotalPages(response.pagination.totalPages);
      
      console.log('useProperties state after update:', {
        propertiesLength: response.data.length,
        totalCount: response.pagination.totalCount,
        currentPage: resetPage ? 1 : response.pagination.currentPage
      });
      
      // Add to recent searches only for new searches
      if (resetPage) {
        addRecentSearch(convertedFilters);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search properties');
      setProperties([]);
      setTotalCount(0);
      setTotalPages(0);
    } finally {
      setIsLoading(false);
    }
  }, [addRecentSearch, currentPage, convertPriceFilters]);

  const loadMore = useCallback(async () => {
    if (!currentFilters || currentPage >= totalPages || isLoading) return;

    setIsLoading(true);
    try {
      const response = await propertyService.searchProperties(currentFilters, currentPage + 1, 20);
      setProperties(prev => [...prev, ...response.data]);
      setCurrentPage(response.pagination.currentPage);
      setTotalPages(response.pagination.totalPages);
      setTotalCount(response.pagination.totalCount);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load more properties');
    } finally {
      setIsLoading(false);
    }
  }, [currentFilters, currentPage, totalPages, isLoading]);

  const goToPage = useCallback(async (page: number) => {
    if (!currentFilters || page < 1 || page > totalPages || page === currentPage) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await propertyService.searchProperties(currentFilters, page, 20);
      setProperties(response.data);
      setCurrentPage(response.pagination.currentPage);
      setTotalPages(response.pagination.totalPages);
      setTotalCount(response.pagination.totalCount);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load properties');
    } finally {
      setIsLoading(false);
    }
  }, [currentFilters, totalPages, currentPage]);

  const refetch = useCallback(async () => {
    if (!currentFilters) return;
    await searchProperties(currentFilters);
  }, [currentFilters, searchProperties]);

  // Note: We don't refetch when currency changes because the backend returns both GEL and USD amounts
  // The currency display is handled by the CurrencyContext.formatPrice() function in the UI components

  return {
    properties,
    totalCount,
    currentPage,
    totalPages,
    isLoading,
    error,
    searchProperties,
    loadMore,
    goToPage,
    refetch,
  };
};

export const useProperty = (id?: string): UsePropertyReturn => {
  const [property, setProperty] = useState<Property | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProperty = useCallback(async (propertyId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await propertyService.getProperty(propertyId);
      setProperty(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch property');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProperty = useCallback(async (propertyId: string, data: Partial<Property>) => {
    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setProperty(prev => prev ? { ...prev, ...data } : null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update property');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteProperty = useCallback(async (propertyId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setProperty(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete property');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (id) {
      fetchProperty(id);
    }
  }, [id, fetchProperty]);

  return {
    property,
    isLoading,
    error,
    fetchProperty,
    updateProperty,
    deleteProperty,
  };
};

export const useFavorites = (): UseFavoritesReturn => {
  const [favorites, setFavorites] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { toggleFavorite: toggleFavoriteInContext } = useAppContext();

  useEffect(() => {
    const loadFavorites = async () => {
      setIsLoading(true);
      try {
        const favoriteIds = await userService.getFavorites();
        setFavorites(favoriteIds);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load favorites');
      } finally {
        setIsLoading(false);
      }
    };

    loadFavorites();
  }, []);

  const addToFavorites = useCallback(async (propertyId: string) => {
    try {
      await userService.addToFavorites(propertyId);
      setFavorites(prev => [...prev, propertyId]);
      toggleFavoriteInContext(propertyId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add to favorites');
    }
  }, [toggleFavoriteInContext]);

  const removeFromFavorites = useCallback(async (propertyId: string) => {
    try {
      await userService.removeFromFavorites(propertyId);
      setFavorites(prev => prev.filter(id => id !== propertyId));
      toggleFavoriteInContext(propertyId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove from favorites');
    }
  }, [toggleFavoriteInContext]);

  const isFavorite = useCallback((propertyId: string) => {
    return favorites.includes(propertyId);
  }, [favorites]);

  return {
    favorites,
    isLoading,
    error,
    addToFavorites,
    removeFromFavorites,
    isFavorite,
  };
};
