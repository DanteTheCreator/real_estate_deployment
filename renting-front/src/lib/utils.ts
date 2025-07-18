import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// MinIO Image URL utilities
export const getMinioImageUrl = (imagePath: string | null | undefined): string => {
  if (!imagePath) {
    return '/placeholder.svg';
  }
  
  // If it's already a full URL, return as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // If it's a relative path, construct MinIO URL
  const minioUrl = import.meta.env.VITE_MINIO_URL || 'http://localhost:9000';
  const minioBucket = import.meta.env.VITE_MINIO_BUCKET || 'property-images';
  
  // Remove leading slash if present
  const cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath;
  
  return `${minioUrl}/${minioBucket}/${cleanPath}`;
};

export const getMinioImageUrls = (images: string[] | null | undefined): string[] => {
  if (!images || images.length === 0) {
    return ['/placeholder.svg'];
  }
  
  return images.map(image => getMinioImageUrl(image));
};
