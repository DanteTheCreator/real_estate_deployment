import React, { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Search, Filter, X, MapPin, Home, DollarSign, Settings, ChevronDown, SlidersHorizontal } from 'lucide-react';
import { SearchFilters } from '@/types';

interface AdvancedSearchPanelProps {
  onSearch?: (filters: SearchFilters) => void;
}

interface FilterState {
  dealType: string;
  propertyType: string;
  location: string;
  minArea: string;
  maxArea: string;
  areaRange: number[];
  minPrice: string;
  maxPrice: string;
  priceRange: number[];
  currency: string;
  rooms: string;
  bathrooms: string;
  floors: string;
  condition: string;
  parking: boolean;
  balcony: boolean;
  elevator: boolean;
  furnished: boolean;
  // Additional filters
  applicationType: string[];
  status: string[];
  bedroomsFrom: string;
  bedroomsTo: string;
  livingAreaFrom: string;
  livingAreaTo: string;
  yardAreaFrom: string;
  yardAreaTo: string;
  centralheating: boolean;
  naturalgas: boolean;
  garage: boolean;
  storageroom: boolean;
  basement: boolean;
  drinkingwater: boolean;
  pool: boolean;
  videocall: boolean;
  ukraineDiscount: boolean;
  cadastralCode: string;
}

const AdvancedSearchPanel: React.FC<AdvancedSearchPanelProps> = ({ onSearch }) => {
  const [filters, setFilters] = useState<FilterState>({
    dealType: 'sale',
    propertyType: '',
    location: '',
    minArea: '',
    maxArea: '',
    areaRange: [0, 500],
    minPrice: '',
    maxPrice: '',
    priceRange: [0, 1000000],
    currency: 'gel',
    rooms: '',
    bathrooms: '',
    floors: '',
    condition: '',
    parking: false,
    balcony: false,
    elevator: false,
    furnished: false,
    // Additional filters
    applicationType: [],
    status: [],
    bedroomsFrom: '',
    bedroomsTo: '',
    livingAreaFrom: '',
    livingAreaTo: '',
    yardAreaFrom: '',
    yardAreaTo: '',
    centralheating: false,
    naturalgas: false,
    garage: false,
    storageroom: false,
    basement: false,
    drinkingwater: false,
    pool: false,
    videocall: false,
    ukraineDiscount: false,
    cadastralCode: ''
  });

  const dealTypes = [
    { value: 'sale', label: 'For sale' },
    { value: 'rent', label: 'For rent' },
    { value: 'leasehold_mortgage', label: 'Leasehold mortgage' },
    { value: 'lease', label: 'For lease' },
    { value: 'daily_rent', label: 'Daily rent' }
  ];

  const propertyTypes = [
    { value: 'apartment', label: 'Apartment' },
    { value: 'house', label: 'House' },
    { value: 'country_house', label: 'Country House' },
    { value: 'land_plot', label: 'Land Plot' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'hotel', label: 'Hotel' },
    { value: 'studio', label: 'Studio' }
  ];

  const handleFilterChange = (key: keyof FilterState, value: string | boolean | number[]) => {
    console.log('Filter change:', key, value); // Debug log
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleCheckboxChange = (key: keyof FilterState, checked: boolean | string) => {
    const boolValue = checked === true || checked === 'true';
    console.log('Checkbox change:', key, boolValue); // Debug log
    setFilters(prev => ({ ...prev, [key]: boolValue }));
  };

  // Calculate active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.propertyType) count++;
    if (filters.location) count++;
    if (filters.minArea || filters.maxArea) count++;
    if (filters.minPrice || filters.maxPrice) count++;
    if (filters.rooms) count++;
    if (filters.bathrooms) count++;
    if (filters.condition) count++;
    if (filters.parking || filters.balcony || filters.elevator || filters.furnished) count++;
    return count;
  }, [filters]);

    // Format currency display
  const formatCurrency = (amount: number) => {
    const symbol = filters.currency === 'usd' ? '₾' : '₾';
    return `${symbol}${amount.toLocaleString()}`;
  };

  const clearFilters = () => {
    setFilters({
      dealType: 'sale',
      propertyType: '',
      location: '',
      minArea: '',
      maxArea: '',
      areaRange: [0, 500],
      minPrice: '',
      maxPrice: '',
      priceRange: [0, 1000000],
      currency: 'gel',
      rooms: '',
      bathrooms: '',
      floors: '',
      condition: '',
      parking: false,
      balcony: false,
      elevator: false,
      furnished: false,
      // Additional filters
      applicationType: [],
      status: [],
      bedroomsFrom: '',
      bedroomsTo: '',
      livingAreaFrom: '',
      livingAreaTo: '',
      yardAreaFrom: '',
      yardAreaTo: '',
      centralheating: false,
      naturalgas: false,
      garage: false,
      storageroom: false,
      basement: false,
      drinkingwater: false,
      pool: false,
      videocall: false,
      ukraineDiscount: false,
      cadastralCode: ''
    });
  };

  const handleArrayFilterChange = (key: 'applicationType' | 'status', value: string) => {
    console.log('Array filter change:', key, value); // Debug log
    setFilters(prev => ({
      ...prev,
      [key]: prev[key].includes(value) 
        ? prev[key].filter(item => item !== value)
        : [...prev[key], value]
    }));
  };

  const handleSearch = () => {
    if (onSearch) {
      // Convert FilterState to SearchFilters
      const searchFilters: SearchFilters = {
        property_type: filters.propertyType || undefined,
        city: filters.location || undefined,
        min_rent: filters.priceRange[0] > 0 ? filters.priceRange[0] : undefined,
        max_rent: filters.priceRange[1] < 1000000 ? filters.priceRange[1] : undefined,
        min_bedrooms: filters.bedroomsFrom ? parseInt(filters.bedroomsFrom) : undefined,
        max_bedrooms: filters.bedroomsTo ? parseInt(filters.bedroomsTo) : undefined,
        areaMin: filters.areaRange[0] > 0 ? filters.areaRange[0] : undefined,
        areaMax: filters.areaRange[1] < 500 ? filters.areaRange[1] : undefined,
        is_furnished: filters.furnished || undefined,
      };
      
      onSearch(searchFilters);
    }
  };

  return (
    <Card className="bg-card shadow-xl -mt-8 relative z-10 mx-4 border-0 rounded-2xl overflow-hidden">
      <CardHeader className="pb-6 bg-gradient-to-r from-primary/5 to-primary/10 border-b border-border">
        <CardTitle className="flex items-center justify-between text-foreground">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Filter className="w-5 h-5 text-primary" />
            </div>
            <span className="text-xl font-semibold">Property Search & Filter</span>
          </div>
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="ml-2 bg-primary/10 text-primary">
              {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''} active
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6 h-12 p-1 bg-muted rounded-xl">
            <TabsTrigger value="basic" className="flex items-center gap-2 data-[state=active]:bg-card data-[state=active]:shadow-sm rounded-lg transition-all">
              <Search className="w-4 h-4" />
              Quick Search
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2 data-[state=active]:bg-card data-[state=active]:shadow-sm rounded-lg transition-all">
              <Settings className="w-4 h-4" />
              Advanced Filters
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="basic" className="space-y-6 mt-0">
            {/* Deal Type Selection */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <Home className="w-4 h-4 text-muted-foreground" />
                <Label className="text-base font-medium text-foreground">Deal Type</Label>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {dealTypes.map((type) => (
                  <div key={type.value} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                    <input
                      type="radio"
                      id={`deal-type-${type.value}`}
                      name="dealType"
                      value={type.value}
                      checked={filters.dealType === type.value}
                      onChange={() => handleFilterChange('dealType', type.value)}
                      className="w-4 h-4 text-primary border-border focus:ring-2 focus:ring-primary"
                    />
                    <label
                      htmlFor={`deal-type-${type.value}`}
                      className="text-sm font-medium cursor-pointer text-foreground"
                    >
                      {type.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Main Search Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Home className="w-4 h-4" />
                  Property Category
                </Label>
                <Select value={filters.propertyType} onValueChange={(value) => handleFilterChange('propertyType', value)}>
                  <SelectTrigger className="h-11 border-border focus:border-primary focus:ring-primary">
                    <SelectValue placeholder="Select property type" />
                  </SelectTrigger>
                  <SelectContent>
                    {propertyTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Location
                </Label>
                <Input 
                  placeholder="City, district, neighborhood..." 
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                  className="h-11 border-border focus:border-primary focus:ring-primary placeholder:text-muted-foreground"
                />
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <DollarSign className="w-4 h-4" />
                  Currency
                </Label>
                <Select value={filters.currency} onValueChange={(value) => handleFilterChange('currency', value)}>
                  <SelectTrigger className="h-11 border-border focus:border-primary focus:ring-primary">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gel">Georgian Lari (₾)</SelectItem>
                    <SelectItem value="usd">US Dollar (₾)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Area Range Slider */}
            <div className="space-y-4">
              <Label className="text-sm font-medium text-foreground">Area Range (m²)</Label>
              <div className="px-2">
                <Slider
                  value={filters.areaRange}
                  onValueChange={(value) => handleFilterChange('areaRange', value)}
                  max={500}
                  min={0}
                  step={10}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-2">
                  <span>{filters.areaRange[0]} m²</span>
                  <span>{filters.areaRange[1]} m²</span>
                </div>
              </div>
            </div>

            {/* Price Range Slider */}
            <div className="space-y-4">
              <Label className="text-sm font-medium text-foreground">Price Range</Label>
              <div className="px-2">
                <Slider
                  value={filters.priceRange}
                  onValueChange={(value) => handleFilterChange('priceRange', value)}
                  max={1000000}
                  min={0}
                  step={10000}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-2">
                  <span>{formatCurrency(filters.priceRange[0])}</span>
                  <span>{formatCurrency(filters.priceRange[1])}</span>
                </div>
              </div>
            </div>
            
            {/* Search Button */}
            <div className="pt-4">
              <Button 
                onClick={handleSearch}
                className="w-full h-12 bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <Search className="w-5 h-5 mr-2" />
                Search Properties
              </Button>
            </div>
          </TabsContent>
          
          <TabsContent value="advanced" className="space-y-6 mt-0">
            {/* Room & Bathroom Selection */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-medium text-foreground">Bedrooms</Label>
                <Select value={filters.rooms} onValueChange={(value) => handleFilterChange('rooms', value)}>
                  <SelectTrigger className="h-11 border-border focus:border-primary focus:ring-primary">
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 Room</SelectItem>
                    <SelectItem value="2">2 Rooms</SelectItem>
                    <SelectItem value="3">3 Rooms</SelectItem>
                    <SelectItem value="4">4+ Rooms</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium text-foreground">Bathrooms</Label>
                <Select value={filters.bathrooms} onValueChange={(value) => handleFilterChange('bathrooms', value)}>
                  <SelectTrigger className="h-11 border-border focus:border-primary focus:ring-primary">
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 Bathroom</SelectItem>
                    <SelectItem value="2">2 Bathrooms</SelectItem>
                    <SelectItem value="3">3+ Bathrooms</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium text-foreground">Property Condition</Label>
                <Select value={filters.condition} onValueChange={(value) => handleFilterChange('condition', value)}>
                  <SelectTrigger className="h-11 border-border focus:border-primary focus:ring-primary">
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="new">New Construction</SelectItem>
                    <SelectItem value="renovated">Recently Renovated</SelectItem>
                    <SelectItem value="good">Good Condition</SelectItem>
                    <SelectItem value="needs-repair">Needs Renovation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            {/* Amenities */}
            <div className="space-y-4">
              <Label className="text-base font-medium text-foreground">Amenities & Features</Label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                  <input
                    type="checkbox"
                    id="parking"
                    checked={filters.parking}
                    onChange={() => handleCheckboxChange('parking', !filters.parking)}
                    className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                  />
                  <label htmlFor="parking" className="text-sm font-medium cursor-pointer text-foreground">🚗 Parking</label>
                </div>
                <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                  <input
                    type="checkbox"
                    id="balcony"
                    checked={filters.balcony}
                    onChange={() => handleCheckboxChange('balcony', !filters.balcony)}
                    className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                  />
                  <label htmlFor="balcony" className="text-sm font-medium cursor-pointer text-foreground">🌿 Balcony</label>
                </div>
                <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                  <input
                    type="checkbox"
                    id="elevator"
                    checked={filters.elevator}
                    onChange={() => handleCheckboxChange('elevator', !filters.elevator)}
                    className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                  />
                  <label htmlFor="elevator" className="text-sm font-medium cursor-pointer text-foreground">🔼 Elevator</label>
                </div>
                <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                  <input
                    type="checkbox"
                    id="furnished"
                    checked={filters.furnished}
                    onChange={() => handleCheckboxChange('furnished', !filters.furnished)}
                    className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                  />
                  <label htmlFor="furnished" className="text-sm font-medium cursor-pointer text-foreground">🛋️ Furnished</label>
                </div>
              </div>
            </div>
            
            {/* Additional Filters Dialog */}
            <div className="space-y-4">
              <Dialog>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    className="w-full h-12 border-2 border-dashed border-gray-300 hover:border-primary/50 hover:bg-primary/5 text-gray-600 hover:text-primary rounded-xl transition-all duration-200"
                  >
                    <SlidersHorizontal className="w-5 h-5 mr-2" />
                    Additional Filters
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle className="text-xl font-semibold text-slate-800 flex items-center gap-2">
                      <SlidersHorizontal className="w-5 h-5 text-primary" />
                      Additional Filters
                    </DialogTitle>
                  </DialogHeader>
                  
                  <div className="space-y-6 py-4">
                    {/* Application Type */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium text-foreground">Application type</Label>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {['Verified', 'Developer only', 'With photos', 'Only by the owner'].map((type) => {
                          const isSelected = filters.applicationType.includes(type);
                          return (
                            <div key={type} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                              <input
                                type="checkbox"
                                id={`app-type-${type.toLowerCase().replace(/\s+/g, '-')}`}
                                checked={isSelected}
                                onChange={() => handleArrayFilterChange('applicationType', type)}
                                className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                              />
                              <label
                                htmlFor={`app-type-${type.toLowerCase().replace(/\s+/g, '-')}`}
                                className="text-sm font-medium cursor-pointer text-foreground"
                              >
                                {type}
                              </label>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Status */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium text-foreground">Status</Label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {['Not renovated', 'Under renovation', 'Old renovated', 'Renovated', 'Newly renovated', 'Green frame'].map((status) => {
                          const isSelected = filters.status.includes(status);
                          return (
                            <div key={status} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                              <input
                                type="checkbox"
                                id={`status-${status.toLowerCase().replace(/\s+/g, '-')}`}
                                checked={isSelected}
                                onChange={() => handleArrayFilterChange('status', status)}
                                className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                              />
                              <label
                                htmlFor={`status-${status.toLowerCase().replace(/\s+/g, '-')}`}
                                className="text-sm font-medium cursor-pointer text-foreground"
                              >
                                {status}
                              </label>
                            </div>
                          );
                        })}
                      </div>
                      <div className="grid grid-cols-2 gap-3 mt-3">
                        {['Black frame', 'White frame'].map((status) => {
                          const isSelected = filters.status.includes(status);
                          return (
                            <div key={status} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                              <input
                                type="checkbox"
                                id={`status-${status.toLowerCase().replace(/\s+/g, '-')}`}
                                checked={isSelected}
                                onChange={() => handleArrayFilterChange('status', status)}
                                className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                              />
                              <label
                                htmlFor={`status-${status.toLowerCase().replace(/\s+/g, '-')}`}
                                className="text-sm font-medium cursor-pointer text-foreground"
                              >
                                {status}
                              </label>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Bedrooms and Living Area */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Bedrooms */}
                      <div className="space-y-3">
                        <Label className="text-sm font-medium text-foreground">Bedrooms</Label>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Input 
                              type="number"
                              placeholder="From"
                              value={filters.bedroomsFrom}
                              onChange={(e) => handleFilterChange('bedroomsFrom', e.target.value)}
                              className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                            />
                          </div>
                          <div className="space-y-2">
                            <Input 
                              type="number"
                              placeholder="To"
                              value={filters.bedroomsTo}
                              onChange={(e) => handleFilterChange('bedroomsTo', e.target.value)}
                              className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Living Area */}
                      <div className="space-y-3">
                        <Label className="text-sm font-medium text-foreground">Living area</Label>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Input 
                              type="number"
                              placeholder="From (m²)"
                              value={filters.livingAreaFrom}
                              onChange={(e) => handleFilterChange('livingAreaFrom', e.target.value)}
                              className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                            />
                          </div>
                          <div className="space-y-2">
                            <Input 
                              type="number"
                              placeholder="To (m²)"
                              value={filters.livingAreaTo}
                              onChange={(e) => handleFilterChange('livingAreaTo', e.target.value)}
                              className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Yard Area */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium text-foreground">Yard area</Label>
                      <div className="grid grid-cols-2 gap-4 max-w-md">
                        <div className="space-y-2">
                          <Input 
                            type="number"
                            placeholder="From (m²)"
                            value={filters.yardAreaFrom}
                            onChange={(e) => handleFilterChange('yardAreaFrom', e.target.value)}
                            className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                          />
                        </div>
                        <div className="space-y-2">
                          <Input 
                            type="number"
                            placeholder="To (m²)"
                            value={filters.yardAreaTo}
                            onChange={(e) => handleFilterChange('yardAreaTo', e.target.value)}
                            className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Additional Information */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium text-foreground">Additional information</Label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {[
                          'Central heating',
                          'Natural gas', 
                          'Garage',
                          'Storage room',
                          'Basement',
                          'Drinking water',
                          'Pool',
                          'Video call'
                        ].map((item) => {
                          const key = item.toLowerCase().replace(/\s+/g, '') as keyof FilterState;
                          const isSelected = filters[key] as boolean;
                          return (
                            <div key={item} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                              <input
                                type="checkbox"
                                id={`checkbox-${key}`}
                                checked={isSelected}
                                onChange={() => handleFilterChange(key, !isSelected)}
                                className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                              />
                              <label
                                htmlFor={`checkbox-${key}`}
                                className="text-sm font-medium cursor-pointer text-foreground"
                              >
                                {item}
                              </label>
                            </div>
                          );
                        })}
                      </div>
                      
                      {/* Ukraine Discount - Special styling */}
                      <div className="mt-3">
                        <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all max-w-xs">
                          <input
                            type="checkbox"
                            id="checkbox-ukraineDiscount"
                            checked={filters.ukraineDiscount}
                            onChange={() => handleFilterChange('ukraineDiscount', !filters.ukraineDiscount)}
                            className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                          />
                          <label
                            htmlFor="checkbox-ukraineDiscount"
                            className="text-sm font-medium cursor-pointer text-foreground"
                          >
                            🇺🇦 Discount for citizens of Ukraine
                          </label>
                        </div>
                      </div>
                    </div>

                    {/* Cadastral Code */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium text-foreground">Cadastral code</Label>
                      <Input 
                        placeholder="Enter cadastral code"
                        value={filters.cadastralCode}
                        onChange={(e) => handleFilterChange('cadastralCode', e.target.value)}
                        className="h-11 border-border focus:border-primary focus:ring-primary max-w-md"
                      />
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            
            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t border-border">
              <Button 
                onClick={handleSearch}
                className="flex-1 h-12 bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <Search className="w-5 h-5 mr-2" />
                Apply Filters
              </Button>
              <Button 
                variant="outline" 
                onClick={clearFilters}
                className="h-12 px-6 border-border hover:bg-muted rounded-xl transition-all duration-200"
              >
                <X className="w-4 h-4 mr-2" />
                Clear All
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export { AdvancedSearchPanel };
export default AdvancedSearchPanel;