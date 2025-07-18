import { apiService } from './apiService';
import { API_ENDPOINTS, PropertyImage } from '@/types';

export const minioService = {
  async uploadImages(images: File[]): Promise<string[]> {
    const formData = new FormData();
    images.forEach((image) => {
      formData.append('files', image);
    });

    try {
      const response = await apiService.post<{ files: Array<{ url: string }> }>(
        API_ENDPOINTS.MINIO_UPLOAD,
        formData
        // Don't set Content-Type header - let browser set it automatically with boundary
      );
      
      return response.files.map(file => file.url);
    } catch (error) {
      console.error('Error uploading images to MinIO:', error);
      throw new Error('Failed to upload images');
    }
  },

  async deleteImage(imagePath: string): Promise<void> {
    try {
      await apiService.delete(API_ENDPOINTS.MINIO_DELETE(imagePath));
    } catch (error) {
      console.error('Error deleting image from MinIO:', error);
      throw new Error('Failed to delete image');
    }
  },

  getImageUrl(image: PropertyImage | string | null | undefined): string {
    if (!image) {
      return '/placeholder.svg';
    }
    
    // Handle PropertyImage object from API
    if (typeof image === 'object' && image.image_url) {
      return image.image_url;
    }
    
    // Handle string URL (legacy support or direct URLs)
    if (typeof image === 'string') {
      // If it's already a full URL, return as is
      if (image.startsWith('http://') || image.startsWith('https://')) {
        return image;
      }
      
      // If it's a relative path, construct MinIO URL
      const minioUrl = import.meta.env.VITE_MINIO_URL || 'http://127.0.0.1:9000';
      const minioBucket = import.meta.env.VITE_MINIO_BUCKET || 'real-estate';
      
      // Remove leading slash if present
      const cleanPath = image.startsWith('/') ? image.slice(1) : image;
      
      return `${minioUrl}/${minioBucket}/${cleanPath}`;
    }
    
    return '/placeholder.svg';
  },

  getImageUrls(images: PropertyImage[] | string[] | null | undefined): string[] {
    if (!images || images.length === 0) {
      return ['/placeholder.svg'];
    }
    
    return images.map(image => this.getImageUrl(image));
  },

  getPrimaryImage(images: PropertyImage[] | null | undefined): PropertyImage | null {
    if (!images || images.length === 0) {
      return null;
    }
    
    // Find the primary image
    const primary = images.find(img => img.is_primary);
    if (primary) {
      return primary;
    }
    
    // If no primary image, return the first one ordered by order_index
    return images.sort((a, b) => a.order_index - b.order_index)[0];
  },

  getOrderedImages(images: PropertyImage[] | null | undefined): PropertyImage[] {
    if (!images || images.length === 0) {
      return [];
    }
    
    // Sort images by order_index, then by is_primary (primary first if same order)
    return images.sort((a, b) => {
      if (a.order_index !== b.order_index) {
        return a.order_index - b.order_index;
      }
      return b.is_primary ? 1 : a.is_primary ? -1 : 0;
    });
  }
};
