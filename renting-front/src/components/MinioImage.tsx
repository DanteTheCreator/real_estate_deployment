import React, { useState } from 'react';
import { PropertyImage } from '@/types';
import { minioService } from '@/services';

interface MinioImageProps {
  image: PropertyImage | string | null | undefined;
  alt?: string;
  className?: string;
  fallbackSrc?: string;
  onError?: () => void;
  onClick?: () => void;
}

const MinioImage: React.FC<MinioImageProps> = ({
  image,
  alt,
  className = '',
  fallbackSrc = '/placeholder.svg',
  onError,
  onClick
}) => {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const imageUrl = hasError ? fallbackSrc : minioService.getImageUrl(image);
  const imageAlt = alt || (typeof image === 'object' && image?.caption) || 'Property image';

  const handleError = () => {
    setHasError(true);
    setIsLoading(false);
    onError?.();
  };

  const handleLoad = () => {
    setIsLoading(false);
  };

  return (
    <div className={`relative ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded" />
      )}
      <img
        src={imageUrl}
        alt={imageAlt}
        className={`w-full h-full object-cover ${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-200`}
        onError={handleError}
        onLoad={handleLoad}
        onClick={onClick}
      />
    </div>
  );
};

export default MinioImage;