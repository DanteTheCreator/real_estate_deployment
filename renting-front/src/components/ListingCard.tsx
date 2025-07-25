import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Heart, MapPin, Bed, Bath, Square, Loader2 } from 'lucide-react';
import { Property } from '@/types';
import { minioService, propertyService } from '@/services';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { useToast } from '@/hooks/use-toast';

interface ListingCardProps {
  property: Property;
}

const ListingCard: React.FC<ListingCardProps> = ({ property }) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const { t } = useLanguage();
  const { formatPrice } = useCurrency();
  const [isSaved, setIsSaved] = useState(false);
  const [savingProperty, setSavingProperty] = useState(false);

  useEffect(() => {
    const checkSavedStatus = async () => {
      if (user && property.id) {
        try {
          const saved = await propertyService.checkIfSaved(property.id.toString());
          setIsSaved(saved);
        } catch (error) {
          console.error('Error checking if property is saved:', error);
        }
      }
    };

    checkSavedStatus();
  }, [user, property.id]);

  const handleSaveProperty = async (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent Link navigation
    e.stopPropagation(); // Prevent event bubbling

    if (!user) {
      // Open sign-in page in new tab instead of showing error
      window.open('/auth', '_blank');
      return;
    }

    try {
      setSavingProperty(true);
      
      const response = await propertyService.toggleSaveProperty(property.id.toString());
      const wasSaved = isSaved;
      setIsSaved(!wasSaved);
      
      toast({
        title: wasSaved ? t('common.propertyRemoved') : t('common.propertySaved'),
        description: response.message,
      });
    } catch (error) {
      console.error('Error saving/unsaving property:', error);
      toast({
        title: t('common.error'),
        description: t('common.saveFailed'),
        variant: "destructive",
      });
    } finally {
      setSavingProperty(false);
    }
  };

  const formatAddress = (property: Property) => {
    return `${property.address}, ${property.city}, ${property.state}`;
  };

  return (
    <Link to={`/property/${property.id}`}>
      <Card className="group hover:shadow-lg transition-shadow duration-300 bg-white">
        <div className="relative">
          <div className="aspect-[4/3] bg-gray-200 rounded-t-lg overflow-hidden">
            <img
              src={minioService.getImageUrl(minioService.getPrimaryImage(property.images))}
              alt={property.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
          
          <div className="absolute top-3 left-3 flex gap-2">
            {property.property_type === 'studio' && (
              <Badge variant="secondary" className="bg-blue-600 text-white">
                Studio
              </Badge>
            )}
            {property.property_type === 'apartment' && (
              <Badge variant="secondary" className="bg-green-600 text-white">
                Apartment
              </Badge>
            )}
            {property.property_type === 'house' && (
              <Badge variant="secondary" className="bg-purple-600 text-white">
                House
              </Badge>
            )}
            {property.property_type === 'condo' && (
              <Badge variant="secondary" className="bg-orange-600 text-white">
                Condo
              </Badge>
            )}
            {property.property_type === 'townhouse' && (
              <Badge variant="secondary" className="bg-indigo-600 text-white">
                Townhouse
              </Badge>
            )}
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-3 right-3 h-8 w-8 bg-white/80 hover:bg-white text-gray-600 hover:text-red-600"
            onClick={handleSaveProperty}
            disabled={savingProperty}
          >
            {savingProperty ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Heart className={`h-4 w-4 ${isSaved ? 'fill-red-500 text-red-500' : ''}`} />
            )}
          </Button>
        </div>
        
        <CardContent className="p-4">
          <div className="space-y-3">
            <div>
              <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-blue-600 transition-colors">
                {property.title}
              </h3>
              <div className="flex items-center text-sm text-gray-600 mt-1">
                <MapPin className="h-4 w-4 mr-1" />
                <span className="line-clamp-1">{formatAddress(property)}</span>
              </div>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-gray-600">
              {property.bedrooms > 0 && (
                <div className="flex items-center">
                  <Bed className="h-4 w-4 mr-1" />
                  <span>{property.bedrooms} bed{property.bedrooms > 1 ? 's' : ''}</span>
                </div>
              )}
              <div className="flex items-center">
                <Bath className="h-4 w-4 mr-1" />
                <span>{property.bathrooms} bath{property.bathrooms > 1 ? 's' : ''}</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xl font-bold text-gray-900">
                  {formatPrice(property.rent_amount, property.rent_amount_usd, property.listing_type)}
                </div>
                <div className="text-sm text-gray-600">per month</div>
              </div>
              
              <Badge 
                variant={property.is_available ? "default" : "secondary"}
                className={property.is_available ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}
              >
                {property.is_available ? "Available" : "Not Available"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};

export default ListingCard;
