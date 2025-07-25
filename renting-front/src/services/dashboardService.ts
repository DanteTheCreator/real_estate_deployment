import { apiService } from './apiService';
import { Property, ApiResponse, API_ENDPOINTS } from '@/types';

export interface DashboardStats {
  totalViews: number;
  inquiries: number;
  activeListings: number;
  savedListings: number;
}

export interface MyListing {
  id: number;
  title: string;
  rent_amount: number;
  rent_amount_usd?: number;
  listing_type?: string;
  currency: string;
  status: 'active' | 'draft' | 'inactive' | 'sold' | 'rented';
  views: number;
  created_at: string;
}

export const dashboardService = {
  async getDashboardStats(): Promise<DashboardStats> {
    // For now, return mock data since the endpoint may not exist yet
    return {
      totalViews: 0,
      inquiries: 0,
      activeListings: 0,
      savedListings: 0
    };
  },

  async getMyListings(): Promise<MyListing[]> {
    const response = await apiService.get<Property[]>(
      API_ENDPOINTS.MY_PROPERTIES
    );
    
    // Transform Property to MyListing format
    return response.map(property => ({
      id: property.id,
      title: property.title,
      rent_amount: property.rent_amount,
      currency: 'USD', // Default currency since Property doesn't have currency field
      status: property.is_available ? 'active' : 'inactive',
      views: 0, // Property doesn't have views field yet
      created_at: property.created_at
    }));
  },

  async getSavedListings(): Promise<Property[]> {
    const response = await apiService.get<Property[]>('/properties/saved');
    return response;
  },

  async deleteListing(id: string): Promise<void> {
    await apiService.delete<void>(
      API_ENDPOINTS.PROPERTY_BY_ID(id)
    );
  },

  async toggleFavorite(propertyId: string): Promise<void> {
    await apiService.post<void>(
      `/properties/${propertyId}/toggle-save`,
      {}
    );
  },

  async updateProfile(profileData: {
    first_name?: string;
    last_name?: string;
    email?: string;
    phone?: string;
  }): Promise<void> {
    await apiService.put<void>(
      API_ENDPOINTS.PROFILE,
      profileData
    );
  }
};
