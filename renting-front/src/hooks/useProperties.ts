import { useState, useEffect, useCallback } from 'react';
import { Property, SearchFilters, UsePropertiesReturn, UsePropertyReturn, UseFavoritesReturn } from '@/types';
import { propertyService, userService } from '@/services';
import { useAppContext } from '@/contexts/AppContext';

export const useProperties = (): UsePropertiesReturn => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentFilters, setCurrentFilters] = useState<SearchFilters | null>(null);

  const { addRecentSearch } = useAppContext();

  const searchProperties = useCallback(async (filters: SearchFilters) => {
    setIsLoading(true);
    setError(null);
    setCurrentFilters(filters);

    try {
      const response = await propertyService.searchProperties(filters, 1);
      setProperties(response.data);
      setTotalCount(response.pagination.totalCount);
      setCurrentPage(response.pagination.currentPage);
      setTotalPages(response.pagination.totalPages);
      
      // Add to recent searches
      addRecentSearch(filters);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search properties');
    } finally {
      setIsLoading(false);
    }
  }, [addRecentSearch]);

  const loadMore = useCallback(async () => {
    if (!currentFilters || currentPage >= totalPages) return;

    setIsLoading(true);
    try {
      const response = await propertyService.searchProperties(currentFilters, currentPage + 1);
      setProperties(prev => [...prev, ...response.data]);
      setCurrentPage(response.pagination.currentPage);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load more properties');
    } finally {
      setIsLoading(false);
    }
  }, [currentFilters, currentPage, totalPages]);

  const refetch = useCallback(async () => {
    if (!currentFilters) return;
    await searchProperties(currentFilters);
  }, [currentFilters, searchProperties]);

  return {
    properties,
    totalCount,
    currentPage,
    totalPages,
    isLoading,
    error,
    searchProperties,
    loadMore,
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
