import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '@/components/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { useLanguage } from '@/contexts/LanguageContext';
import { propertyService } from '@/services';
import ImageUpload from '@/components/ImageUpload';

interface PropertyFormData {
  title: string;
  description: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  property_type: 'apartment' | 'house' | 'condo' | 'townhouse' | 'studio';
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  rent_amount: number;
  security_deposit: number;
  lease_duration: number;
  is_furnished: boolean;
  pets_allowed: boolean;
  smoking_allowed: boolean;
  year_built: number;
  parking_spaces: number;
  utilities_included: string;
}

const PostAd: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useLanguage();
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [images, setImages] = useState<string[]>([]);
  
  const [formData, setFormData] = useState<PropertyFormData>({
    title: '',
    description: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    property_type: 'apartment',
    bedrooms: 1,
    bathrooms: 1,
    square_feet: 0,
    rent_amount: 0,
    security_deposit: 0,
    lease_duration: 12,
    is_furnished: false,
    pets_allowed: false,
    smoking_allowed: false,
    year_built: new Date().getFullYear(),
    parking_spaces: 0,
    utilities_included: '',
  });

  const handleInputChange = (field: keyof PropertyFormData, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleImageChange = (newImages: string[]) => {
    setImages(newImages);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.title || !formData.address || !formData.city || !formData.state || !formData.property_type) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    
    try {
      // First create the property (without images)
      const propertyData = {
        ...formData,
      };
      
      const newProperty = await propertyService.createProperty(propertyData);
      
      // Then add images to the property if any were uploaded
      if (images.length > 0) {
        try {
          await propertyService.addPropertyImages(newProperty.id.toString(), images);
        } catch (imageError) {
          console.warn('Property created but failed to add images:', imageError);
          // Don't fail the entire process if images fail
        }
      }
      
      toast({
        title: "Success!",
        description: "Your property has been posted successfully.",
      });
      
      navigate(`/property/${newProperty.id}`);
    } catch (error) {
      console.error('Error creating property:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create property. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-slate-800 mb-6">Post Your Property</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-slate-800">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="title">Property Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="e.g. Beautiful 2BR Apartment in Downtown"
                  required
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe your property..."
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="property_type">Property Type *</Label>
                  <Select
                    value={formData.property_type}
                    onValueChange={(value) => handleInputChange('property_type', value as PropertyFormData['property_type'])}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="apartment">Apartment</SelectItem>
                      <SelectItem value="house">House</SelectItem>
                      <SelectItem value="condo">Condo</SelectItem>
                      <SelectItem value="townhouse">Townhouse</SelectItem>
                      <SelectItem value="studio">Studio</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="rent_amount">Monthly Rent ($) *</Label>
                  <Input
                    id="rent_amount"
                    type="number"
                    value={formData.rent_amount === 0 ? '' : formData.rent_amount}
                    onChange={(e) => {
                      const value = e.target.value;
                      handleInputChange('rent_amount', value === '' ? 0 : parseFloat(value) || 0);
                    }}
                    min="0"
                    placeholder="Enter monthly rent amount"
                    required
                    className="[&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-slate-800">Location</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="address">Street Address *</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  placeholder="123 Main Street"
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="city">City *</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => handleInputChange('city', e.target.value)}
                    placeholder="City"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="state">State *</Label>
                  <Input
                    id="state"
                    value={formData.state}
                    onChange={(e) => handleInputChange('state', e.target.value)}
                    placeholder="State"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="zip_code">ZIP Code</Label>
                  <Input
                    id="zip_code"
                    value={formData.zip_code}
                    onChange={(e) => handleInputChange('zip_code', e.target.value)}
                    placeholder="ZIP"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-slate-800">Property Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="bedrooms">Bedrooms</Label>
                  <Input
                    id="bedrooms"
                    type="number"
                    value={formData.bedrooms}
                    onChange={(e) => handleInputChange('bedrooms', parseInt(e.target.value) || 1)}
                    min="0"
                  />
                </div>

                <div>
                  <Label htmlFor="bathrooms">Bathrooms</Label>
                  <Input
                    id="bathrooms"
                    type="number"
                    value={formData.bathrooms}
                    onChange={(e) => handleInputChange('bathrooms', parseInt(e.target.value) || 1)}
                    min="0"
                    step="0.5"
                  />
                </div>

                <div>
                  <Label htmlFor="square_feet">Square Feet</Label>
                  <Input
                    id="square_feet"
                    type="number"
                    value={formData.square_feet}
                    onChange={(e) => handleInputChange('square_feet', parseInt(e.target.value) || 0)}
                    min="0"
                  />
                </div>

                <div>
                  <Label htmlFor="year_built">Year Built</Label>
                  <Input
                    id="year_built"
                    type="number"
                    value={formData.year_built}
                    onChange={(e) => handleInputChange('year_built', parseInt(e.target.value) || new Date().getFullYear())}
                    min="1800"
                    max={new Date().getFullYear() + 1}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="security_deposit">Security Deposit ($)</Label>
                  <Input
                    id="security_deposit"
                    type="number"
                    value={formData.security_deposit === 0 ? '' : formData.security_deposit}
                    onChange={(e) => {
                      const value = e.target.value;
                      handleInputChange('security_deposit', value === '' ? 0 : parseFloat(value) || 0);
                    }}
                    min="0"
                    placeholder="Enter security deposit amount"
                    className="[&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
                  />
                </div>

                <div>
                  <Label htmlFor="lease_duration">Lease Duration (months)</Label>
                  <Input
                    id="lease_duration"
                    type="number"
                    value={formData.lease_duration}
                    onChange={(e) => handleInputChange('lease_duration', parseInt(e.target.value) || 12)}
                    min="1"
                  />
                </div>

                <div>
                  <Label htmlFor="parking_spaces">Parking Spaces</Label>
                  <Input
                    id="parking_spaces"
                    type="number"
                    value={formData.parking_spaces}
                    onChange={(e) => handleInputChange('parking_spaces', parseInt(e.target.value) || 0)}
                    min="0"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="utilities_included">Utilities Included</Label>
                <Input
                  id="utilities_included"
                  value={formData.utilities_included}
                  onChange={(e) => handleInputChange('utilities_included', e.target.value)}
                  placeholder="e.g. Water, Heat, Internet"
                />
              </div>

              <div className="flex flex-wrap gap-6">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="is_furnished"
                    checked={formData.is_furnished}
                    onCheckedChange={(checked) => handleInputChange('is_furnished', !!checked)}
                  />
                  <Label htmlFor="is_furnished">Furnished</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="pets_allowed"
                    checked={formData.pets_allowed}
                    onCheckedChange={(checked) => handleInputChange('pets_allowed', !!checked)}
                  />
                  <Label htmlFor="pets_allowed">Pets Allowed</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="smoking_allowed"
                    checked={formData.smoking_allowed}
                    onCheckedChange={(checked) => handleInputChange('smoking_allowed', !!checked)}
                  />
                  <Label htmlFor="smoking_allowed">Smoking Allowed</Label>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-slate-800">Property Images</CardTitle>
            </CardHeader>
            <CardContent>
              <ImageUpload onImagesChange={handleImageChange} />
              {images.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm text-slate-600">
                    {images.length} image(s) uploaded
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4 pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/dashboard')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Publishing...' : 'Publish Property'}
            </Button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
};

export default PostAd;
