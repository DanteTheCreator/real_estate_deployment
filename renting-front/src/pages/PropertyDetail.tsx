import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AppLayout } from '@/components/AppLayout';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Heart, Share2, Flag, Phone, MapPin, Bed, Bath, Square, ChevronRight, Loader2, Car, Calendar, Home, DollarSign } from 'lucide-react';
import PropertyGallery from '@/components/PropertyGallery';
import { ReportPropertyDialog } from '@/components/ReportPropertyDialog';
import { Property } from '@/types';
import { propertyService, contactService } from '@/services';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useCurrency } from '@/contexts/CurrencyContext';

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const PropertyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const { toast } = useToast();
  const { t } = useLanguage();
  const { formatPrice, currency } = useCurrency();
  const [property, setProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [savingProperty, setSavingProperty] = useState(false);
  const [showReportDialog, setShowReportDialog] = useState(false);

  useEffect(() => {
    const fetchProperty = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const propertyData = await propertyService.getProperty(id);
        setProperty(propertyData);
        
        // Check if property is saved by current user
        if (user) {
          try {
            const saved = await propertyService.checkIfSaved(id);
            setIsSaved(saved);
          } catch (error) {
            console.error('Error checking if property is saved:', error);
          }
        }
      } catch (error) {
        console.error('Error fetching property:', error);
        let errorMsg = 'Failed to load property details';
        if (error instanceof Error) {
          errorMsg = error.message;
        } else if (typeof error === 'string') {
          errorMsg = error;
        } else if (error && typeof error === 'object') {
          try {
            errorMsg = JSON.stringify(error);
          } catch (e) {
            errorMsg = String(error);
          }
        }
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    fetchProperty();
  }, [id, user]);

  const handleSaveProperty = async () => {
    if (!user) {
      // Open sign-in page in new tab instead of showing error
      window.open('/auth', '_blank');
      return;
    }

    if (!property) return;

    try {
      setSavingProperty(true);
      
      const response = await propertyService.toggleSaveProperty(property.id.toString());
      const wasSaved = isSaved;
      setIsSaved(!wasSaved);
      
      toast({
        title: wasSaved ? "Property Removed" : "Property Saved",
        description: response.message,
      });
    } catch (error) {
      console.error('Error saving/unsaving property:', error);
      toast({
        title: "Error",
        description: "Failed to update saved status",
        variant: "destructive",
      });
    } finally {
      setSavingProperty(false);
    }
  };

  const handleShareProperty = async () => {
    if (!property) return;

    try {
      const success = await contactService.shareProperty(
        property.id.toString(),
        property.title,
        property.price
      );

      if (success) {
        toast({
          title: "Property Link Shared",
          description: "The property link has been copied to your clipboard or shared via your device.",
        });
      } else {
        // Fallback: show the link in a toast for manual copying
        const shareUrl = contactService.generateShareLink(property.id.toString(), property.title);
        toast({
          title: "Share this property",
          description: shareUrl,
          duration: 8000,
        });
      }
    } catch (error) {
      console.error('Error sharing property:', error);
      toast({
        title: "Error",
        description: "Failed to share property. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleFlagProperty = () => {
    setShowReportDialog(true);
  };

  const handleAddressClick = () => {
    if (!property) return;

    // Construct the full address for Google Maps search
    const fullAddress = [
      property.address,
      property.city,
      property.state
    ].filter(Boolean).join(', ');

    // Create Google Maps search URL
    const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(fullAddress)}`;
    
    // Open in new tab
    window.open(googleMapsUrl, '_blank');
  };

  const handleScheduleViewing = () => {
    if (!property) return;
    
    const propertyUrl = window.location.href;
    const subject = `Schedule Property Viewing - ${property.title}`;
    const body = `Hello ComfyRent Team,

I would like to schedule a viewing for the following property:

Property: ${property.title}
Address: ${property.address}, ${property.city}, ${property.state}
${property.listing_type === 'sale' ? 'Price' : 'Rent'}: ${formatPrice(property.rent_amount || 0, property.rent_amount_usd, property.listing_type)}
Property URL: ${propertyUrl}

Please contact me to arrange a convenient viewing time.

Thank you!`;

    // Create mailto link
    const mailtoLink = `mailto:info.nextep.solutions@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.open(mailtoLink, '_blank');
    
    toast({
      title: "Email Client Opened",
      description: "Please send the email to schedule your viewing",
    });
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex justify-center items-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </AppLayout>
    );
  }

  if (error || !property) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Property Not Found</h1>
          <p className="text-gray-600 mb-6">{error || 'The property you are looking for does not exist.'}</p>
          <div className="text-left max-w-xl mx-auto bg-gray-100 rounded p-4 text-xs text-red-700">
            <strong>Debug Info:</strong>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
              {JSON.stringify({ id, error, property }, null, 2)}
            </pre>
          </div>
          <Link to="/listings">
            <Button>{t('property.back')}</Button>
          </Link>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-6">
          <Link to="/" className="hover:text-gray-700">Home</Link>
          <ChevronRight className="h-4 w-4" />
          <Link to="/listings" className="hover:text-gray-700">Listings</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">{property.title}</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Images and Details */}
          <div className="lg:col-span-2">
            {/* Property Gallery */}
            <div className="mb-8">
              <PropertyGallery images={property.images || []} title={property.title} />
            </div>

            {/* Property Info */}
            <div className="space-y-6">
              {/* Title and Price */}
              <div>
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">{property.title}</h1>
                    <div 
                      className="flex items-center text-gray-600 mb-3 cursor-pointer hover:text-blue-600 transition-colors group" 
                      onClick={handleAddressClick}
                      title="Click to view on Google Maps"
                    >
                      <MapPin className="h-4 w-4 mr-1 group-hover:text-blue-600" />
                      <span className="underline-offset-2 group-hover:underline">{property.address}, {property.city}</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-3xl font-bold text-blue-600">
                        {formatPrice(property.rent_amount || 0, property.rent_amount_usd, property.listing_type)}
                      </span>
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        {property.is_available ? 'Available' : 'Not Available'}
                      </Badge>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleSaveProperty}
                      disabled={savingProperty}
                      className="h-10 w-10"
                    >
                      {savingProperty ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Heart className={`h-4 w-4 ${isSaved ? 'fill-red-500 text-red-500' : ''}`} />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleShareProperty}
                      className="h-10 w-10"
                      title="Share this property"
                    >
                      <Share2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleFlagProperty}
                      className="h-10 w-10"
                      title="Report this property"
                    >
                      <Flag className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Key Features */}
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Property Features</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="flex items-center space-x-2">
                      <Bed className="h-5 w-5 text-gray-500" />
                      <span className="text-sm text-gray-600">{property.bedrooms} Bedrooms</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Bath className="h-5 w-5 text-gray-500" />
                      <span className="text-sm text-gray-600">{property.bathrooms} Bathrooms</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Square className="h-5 w-5 text-gray-500" />
                      <span className="text-sm text-gray-600">{property.square_feet || 'N/A'} sq ft</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Home className="h-5 w-5 text-gray-500" />
                      <span className="text-sm text-gray-600">{property.property_type}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Description */}
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Description</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {property.description || 'No description available for this property.'}
                  </p>
                </CardContent>
              </Card>

              {/* Additional Details */}
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Property Details</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-gray-500" />
                      <span className="text-sm text-gray-600">Available from: {formatDate(property.created_at)}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <DollarSign className="h-4 w-4 text-gray-500" />
                      <span className="text-sm text-gray-600">Deposit: {formatPrice(property.security_deposit || (property.rent_amount * 2), property.rent_amount_usd ? (property.rent_amount_usd * 2) : undefined, 'sale')}</span>
                    </div>
                    {property.amenities && property.amenities.length > 0 && (
                      <div className="md:col-span-2">
                        <span className="text-sm font-medium text-gray-900">Amenities: </span>
                        <span className="text-sm text-gray-600">{property.amenities.map(amenity => amenity.name).join(', ')}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Right Column - Contact Card */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <Card>
                <CardContent className="p-6">
                  <div className="text-center mb-6">
                    <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4 p-2">
                      <img 
                        src="/logo-comfyrent.svg" 
                        alt="ComfyRent Logo" 
                        className="w-full h-full object-contain"
                      />
                    </div>
                    <h3 className="text-lg font-semibold">Contact ComfyRent</h3>
                    <p className="text-sm text-gray-600 mt-1">Get in touch about this property</p>
                  </div>

                  <div className="space-y-3">
                    <Button 
                      className="w-full" 
                      size="lg"
                      onClick={() => window.location.href = 'tel:+995599738023'}
                    >
                      <Phone className="h-4 w-4 mr-2" />
                      Call ComfyRent
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full" 
                      size="lg"
                      onClick={handleSaveProperty}
                      disabled={savingProperty}
                    >
                      {savingProperty ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Heart className={`h-4 w-4 mr-2 ${isSaved ? 'fill-red-500 text-red-500' : ''}`} />
                      )}
                      {isSaved ? 'Remove from Saved' : 'Save Listing'}
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full" 
                      size="lg"
                      onClick={handleScheduleViewing}
                    >
                      Schedule Viewing
                    </Button>
                  </div>

                  <div className="mt-6 pt-6 border-t">
                    <div className="text-sm text-gray-600 space-y-2">
                      <p><strong>Property ID:</strong> #{property.id}</p>
                      <p><strong>Listed:</strong> {formatDate(property.created_at)}</p>
                      <p><strong>Views:</strong> 127 this week</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Similar Properties */}
              <Card className="mt-6">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Similar Properties</h3>
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded">
                      <div className="font-medium">Modern 2BR Apartment</div>
                      <div>Downtown • {formatPrice(2800, 1000, 'rent')}</div>
                    </div>
                    <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded">
                      <div className="font-medium">Luxury Studio</div>
                      <div>Midtown • {formatPrice(2200, 800, 'rent')}</div>
                    </div>
                  </div>
                  <Button variant="outline" className="w-full mt-4">
                    View All Similar
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
      
      {/* Report Property Dialog */}
      {property && (
        <ReportPropertyDialog
          isOpen={showReportDialog}
          onClose={() => setShowReportDialog(false)}
          propertyId={property.id.toString()}
          propertyTitle={property.title}
        />
      )}
    </AppLayout>
  );
};

export default PropertyDetail;
