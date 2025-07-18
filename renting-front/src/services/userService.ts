import { apiService } from './apiService';
import { User, ApiResponse, API_ENDPOINTS } from '@/types';

export const userService = {
  async getProfile(): Promise<User> {
    const response = await apiService.get<User>(API_ENDPOINTS.PROFILE);
    return response;
  },

  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiService.put<User>(
      API_ENDPOINTS.PROFILE,
      userData
    );
    return response;
  },

  async getFavorites(): Promise<string[]> {
    const response = await apiService.get<string[]>(API_ENDPOINTS.FAVORITES);
    return response;
  },

  async addToFavorites(propertyId: string): Promise<void> {
    await apiService.post<void>(
      `${API_ENDPOINTS.FAVORITES}/${propertyId}`
    );
  },

  async removeFromFavorites(propertyId: string): Promise<void> {
    await apiService.delete<void>(
      `${API_ENDPOINTS.FAVORITES}/${propertyId}`
    );
  },

  async getNotifications(): Promise<Notification[]> {
    const response = await apiService.get<Notification[]>(
      API_ENDPOINTS.NOTIFICATIONS
    );
    return response;
  },

  async markNotificationAsRead(notificationId: string): Promise<void> {
    await apiService.patch<void>(
      `${API_ENDPOINTS.NOTIFICATIONS}/${notificationId}`,
      { read: true }
    );
  },

  async uploadAvatar(file: File): Promise<string> {
    const response = await apiService.uploadFile<{ url: string }>(
      `${API_ENDPOINTS.PROFILE}/avatar`,
      file
    );
    return response.url;
  },
};
