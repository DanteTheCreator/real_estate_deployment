import React, { useState, useEffect } from 'react';
import ListingCard from './ListingCard';
import { Property } from '@/types';
import { propertyService } from '@/services';
import { Loader2 } from 'lucide-react';

interface ListingGridProps {
  properties?: Property[];
  loading?: boolean;
  error?: string | null;
}

const ListingGrid: React.FC<ListingGridProps> = ({ 
  properties: propProperties, 
  loading: propLoading, 
  error: propError 
}) => {
  const [properties, setProperties] = useState<Property[]>(propProperties || []);
  const [loading, setLoading] = useState(propLoading || false);
  const [error, setError] = useState<string | null>(propError || null);

  useEffect(() => {
    // If properties are passed as props, use those
    if (propProperties !== undefined) {
      setProperties(propProperties);
      setLoading(propLoading || false);
      setError(propError || null);
      return;
    }

    // Otherwise, fetch properties
    const fetchProperties = async () => {
      try {
        setLoading(true);
        console.log('Fetching properties...');
        const response = await propertyService.getProperties(1, 12);
        console.log('Properties response:', response);
        setProperties(response.data);
      } catch (err) {
        console.error('Error fetching properties:', err);
        setError(err instanceof Error ? err.message : 'Failed to load properties');
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, [propProperties, propLoading, propError]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading properties...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error: {error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (properties.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground text-lg">No properties found.</p>
        <p className="text-sm text-muted-foreground mt-2">
          Try adjusting your search criteria or check back later for new listings.
        </p>
      </div>
    );
  }

  return (
    <div>      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {properties.map((property) => (
          <ListingCard key={property.id} property={property} />
        ))}
      </div>
    </div>
  );
};

export { ListingGrid };
export default ListingGrid;