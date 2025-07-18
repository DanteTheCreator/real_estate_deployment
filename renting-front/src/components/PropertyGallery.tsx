import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { minioService } from '@/services';
import { PropertyImage } from '@/types';

interface PropertyGalleryProps {
  images: PropertyImage[];
  title: string;
}

const PropertyGallery: React.FC<PropertyGalleryProps> = ({ images, title }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const openLightbox = (index: number) => {
    setCurrentIndex(index);
    setIsLightboxOpen(true);
  };

  // Get ordered images (primary first, then by order_index)
  const orderedImages = minioService.getOrderedImages(images);
  const displayImages = orderedImages.map(img => minioService.getImageUrl(img));

  return (
    <>
      <div className="relative">
        {/* Main Image */}
        <div 
          className="bg-slate-200 rounded-lg h-96 flex items-center justify-center relative cursor-pointer overflow-hidden"
          onClick={() => openLightbox(currentIndex)}
        >
          <img 
            src={displayImages[currentIndex]} 
            alt={orderedImages[currentIndex]?.caption || `${title} - Image ${currentIndex + 1}`}
            className="w-full h-full object-cover"
          />
          
          {/* Navigation Arrows */}
          <Button
            variant="ghost"
            size="sm"
            className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2"
            onClick={(e) => {
              e.stopPropagation();
              prevImage();
            }}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2"
            onClick={(e) => {
              e.stopPropagation();
              nextImage();
            }}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
          
          {/* Photo Count */}
          <div className="absolute top-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-sm">
            All photos + ({displayImages.length})
          </div>
          
          {/* Dots Indicator */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
            {displayImages.map((_, index) => (
              <button
                key={index}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index === currentIndex ? 'bg-white' : 'bg-white/50'
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentIndex(index);
                }}
              />
            ))}
          </div>
        </div>
        
        {/* Thumbnail Strip */}
        <div className="flex gap-2 mt-4 overflow-x-auto">
          {displayImages.map((image, index) => (
            <button
              key={index}
              className={`flex-shrink-0 w-16 h-16 rounded border-2 overflow-hidden ${
                index === currentIndex ? 'border-blue-600' : 'border-slate-200'
              }`}
              onClick={() => setCurrentIndex(index)}
            >
              <img 
                src={image} 
                alt={orderedImages[index]?.caption || `Thumbnail ${index + 1}`}
                className="w-full h-full object-cover"
              />
            </button>
          ))}
        </div>
      </div>

      {/* Lightbox */}
      {isLightboxOpen && (
        <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center">
          <Button
            variant="ghost"
            size="sm"
            className="absolute top-4 right-4 text-white hover:bg-white/20 p-2"
            onClick={() => setIsLightboxOpen(false)}
          >
            <X className="w-6 h-6" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className="absolute left-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20 p-2"
            onClick={prevImage}
          >
            <ChevronLeft className="w-6 h-6" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20 p-2"
            onClick={nextImage}
          >
            <ChevronRight className="w-6 h-6" />
          </Button>
          
          <img 
            src={displayImages[currentIndex]} 
            alt={orderedImages[currentIndex]?.caption || `${title} - Image ${currentIndex + 1}`}
            className="max-w-full max-h-full object-contain"
          />
          
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white text-sm">
            {currentIndex + 1} / {displayImages.length}
          </div>
        </div>
      )}
    </>
  );
};

export default PropertyGallery;