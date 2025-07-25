import { apiService } from './apiService';
import { Property, SearchFilters, PaginatedResponse, ApiResponse, API_ENDPOINTS } from '@/types';

export const propertyService = {
  async searchProperties(filters: SearchFilters, page = 1, limit = 20): Promise<PaginatedResponse<Property>> {
    // Convert frontend filters to backend query parameters
    const queryParams: Record<string, string | number | boolean> = {
      skip: (page - 1) * limit,
      limit: Math.min(limit, 500), // Backend max is 500
    };
    
    // Map frontend filter fields to backend query parameters
    if (filters.query) queryParams.query = filters.query;
    if (filters.city) queryParams.city = filters.city;
    if (filters.state) queryParams.state = filters.state;
    if (filters.property_type) {
      queryParams.property_type = filters.property_type;
    } else if (filters.propertyType && filters.propertyType !== 'all') {
      queryParams.property_type = filters.propertyType;
    }
    if (filters.listingType) {
      queryParams.listing_type = filters.listingType;
    }
    if (filters.min_rent || filters.priceMin) {
      queryParams.min_rent = filters.min_rent || filters.priceMin;
    }
    if (filters.max_rent || filters.priceMax) {
      queryParams.max_rent = filters.max_rent || filters.priceMax;
    }
    if (filters.min_bedrooms || filters.bedroomsMin) {
      queryParams.min_bedrooms = filters.min_bedrooms || filters.bedroomsMin;
    }
    if (filters.max_bedrooms || filters.bedroomsMax) {
      queryParams.max_bedrooms = filters.max_bedrooms || filters.bedroomsMax;
    }
    if (filters.pets_allowed !== undefined) queryParams.pets_allowed = filters.pets_allowed;
    if (filters.is_furnished !== undefined) queryParams.is_furnished = filters.is_furnished;
    
    // Currency parameter for filtering
    if (filters.currency) queryParams.currency = filters.currency;
    
    // Additional filters for area search
    if (filters.areaMin) queryParams.min_square_feet = filters.areaMin;
    if (filters.areaMax) queryParams.max_square_feet = filters.areaMax;
    
    // Sort parameters
    queryParams.sort_by = 'date';
    queryParams.sort_order = 'desc';
    
    // Get count parameters (same as query params but without skip/limit)
    const countParams = { ...queryParams };
    delete countParams.skip;
    delete countParams.limit;
    delete countParams.sort_by;
    delete countParams.sort_order;
    
    // Get both properties and total count in parallel
    const [properties, countResponse] = await Promise.all([
      apiService.get<Property[]>(
        `${API_ENDPOINTS.SEARCH_PROPERTIES}${apiService.buildQueryString(queryParams)}`,
        { requiresAuth: false }
      ),
      apiService.get<{ total_count: number }>(
        `${API_ENDPOINTS.SEARCH_PROPERTIES_COUNT}${apiService.buildQueryString(countParams)}`,
        { requiresAuth: false }
      )
    ]);
    
    const totalCount = countResponse.total_count;
    const hasNext = properties.length === limit && (page * limit) < totalCount;
    const totalPages = Math.ceil(totalCount / limit);
    
    return {
      data: properties,
      pagination: {
        currentPage: page,
        totalPages,
        totalCount,
        hasNext,
        hasPrev: page > 1
      }
    };
  },

  async getProperties(page = 1, limit = 20): Promise<PaginatedResponse<Property>> {
    const queryParams = {
      skip: (page - 1) * limit,
      limit: Math.min(limit, 500) // Backend max is 500
    };
    
    // Get both properties and total count in parallel
    const [properties, countResponse] = await Promise.all([
      apiService.get<Property[]>(
        `${API_ENDPOINTS.PROPERTIES}${apiService.buildQueryString(queryParams)}`,
        { requiresAuth: false }
      ),
      apiService.get<{ total_count: number }>(
        API_ENDPOINTS.PROPERTIES_COUNT,
        { requiresAuth: false }
      )
    ]);
    
    const totalCount = countResponse.total_count;
    const hasNext = properties.length === limit && (page * limit) < totalCount;
    const totalPages = Math.ceil(totalCount / limit);
    
    return {
      data: properties,
      pagination: {
        currentPage: page,
        totalPages,
        totalCount,
        hasNext,
        hasPrev: page > 1
      }
    };
  },

  async getProperty(id: string): Promise<Property> {
    const response = await apiService.get<Property>(
      API_ENDPOINTS.PROPERTY_BY_ID(id),
      { requiresAuth: false }
    );
    
    return response;
  },

  async getFeaturedProperties(): Promise<Property[]> {
    // Get more featured properties for better main page display
    const properties = await apiService.get<Property[]>(
      `${API_ENDPOINTS.PROPERTIES}?limit=12&sort_by=date&sort_order=desc`,
      { requiresAuth: false }
    );
    
    return properties;
  },

  async getMyProperties(): Promise<Property[]> {
    const response = await apiService.get<Property[]>(
      API_ENDPOINTS.MY_PROPERTIES
    );
    
    return response;
  },

  async createProperty(propertyData: Partial<Property>): Promise<Property> {
    const response = await apiService.post<Property>(
      API_ENDPOINTS.PROPERTIES,
      propertyData
    );
    
    return response;
  },

  async updateProperty(id: string, propertyData: Partial<Property>): Promise<Property> {
    const response = await apiService.put<Property>(
      API_ENDPOINTS.PROPERTY_BY_ID(id),
      propertyData
    );
    
    return response;
  },

  async deleteProperty(id: string): Promise<void> {
    await apiService.delete<void>(
      API_ENDPOINTS.PROPERTY_BY_ID(id)
    );
  },

  async uploadPropertyImages(propertyId: string, images: File[]): Promise<string[]> {
    const formData = new FormData();
    images.forEach((image, index) => {
      formData.append(`images`, image);
    });

    const response = await apiService.uploadFiles<string[]>(
      `${API_ENDPOINTS.PROPERTY_BY_ID(propertyId)}/images`,
      images
    );
    
    return response;
  },

  async uploadImagesToMinio(images: File[]): Promise<string[]> {
    const formData = new FormData();
    images.forEach((image) => {
      formData.append('images', image);
    });

    // Upload to a general upload endpoint that handles MinIO
    const response = await apiService.post<string[]>(
      '/properties/upload-images',
      formData,
      { 
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    return response;
  },

  async addPropertyImages(propertyId: string, imageUrls: string[]): Promise<void> {
    // Add each image URL to the property
    for (let i = 0; i < imageUrls.length; i++) {
      const imageData = {
        image_url: imageUrls[i],
        caption: '',
        is_primary: i === 0 // First image is primary
      };
      
      await apiService.post<void>(
        `${API_ENDPOINTS.PROPERTY_BY_ID(propertyId)}/images`,
        imageData
      );
    }
  },

  async incrementViews(id: string): Promise<void> {
    await apiService.post<void>(
      `${API_ENDPOINTS.PROPERTY_BY_ID(id)}/view`,
      {},
      { requiresAuth: false }
    );
  },

  async saveProperty(id: string): Promise<void> {
    await apiService.post<void>(
      `${API_ENDPOINTS.PROPERTY_BY_ID(id)}/save`,
      {}
    );
  },

  async unsaveProperty(id: string): Promise<void> {
    await apiService.delete<void>(
      `${API_ENDPOINTS.PROPERTY_BY_ID(id)}/save`
    );
  },

  async toggleSaveProperty(id: string): Promise<{ message: string }> {
    const response = await apiService.post<{ message: string }>(
      `${API_ENDPOINTS.PROPERTY_BY_ID(id)}/toggle-save`,
      {}
    );
    return response;
  },

  async checkIfSaved(id: string): Promise<boolean> {
    try {
      const response = await apiService.get<{ is_saved: boolean }>(
        `${API_ENDPOINTS.PROPERTY_BY_ID(id)}/is-saved`
      );
      return response.is_saved;
    } catch (error) {
      console.error('Error checking if property is saved:', error);
      return false;
    }
  },

  // Utility function to get quick property stats
  async getPropertyStats(): Promise<{ total: number; available: number; cities: string[] }> {
    try {
      // Get a sample of properties to estimate stats
      const response = await apiService.get<Property[]>(
        `${API_ENDPOINTS.PROPERTIES}?limit=100`,
        { requiresAuth: false }
      );
      
      const cities = [...new Set(response.map(p => p.city))].slice(0, 10);
      
      return {
        total: response.length > 99 ? 100 : response.length, // Estimate if we hit limit
        available: response.filter(p => p.is_available).length,
        cities
      };
    } catch (error) {
      console.error('Error fetching property stats:', error);
      return { total: 0, available: 0, cities: [] };
    }
  },
};
