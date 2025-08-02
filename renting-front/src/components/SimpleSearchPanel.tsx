import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Search, Home, Building, MapPin, SlidersHorizontal, DollarSign } from 'lucide-react';
import { LocationSelector } from '@/components/LocationSelector';
import { useProperties } from '@/hooks/useProperties';
import { useAppContext } from '@/contexts/AppContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { SearchFilters } from '@/types';
import { useNavigate } from 'react-router-dom';

interface SimpleSearchPanelProps {
  className?: string;
  onSearch?: (filters: SearchFilters) => void;
}

const SimpleSearchPanel: React.FC<SimpleSearchPanelProps> = ({ className = '', onSearch }) => {
  const navigate = useNavigate();
  const { searchProperties, isLoading } = useProperties();
  const { addNotification } = useAppContext();
  const { t } = useLanguage();
  
  // Search form state
  const [searchForm, setSearchForm] = useState<SearchFilters>({
    query: '',
    propertyType: 'all', // Changed from empty string to 'all'
    listingType: 'sale',
    location: '',
    selectedLocations: [], // New field for hierarchical location selection
    priceMin: undefined,
    priceMax: undefined,
    currency: 'GEL',
    areaMin: undefined,
    areaMax: undefined,
    bedroomsMin: undefined,
    bedroomsMax: undefined,
    yardAreaMin: undefined,
    yardAreaMax: undefined,
    status: [],
    features: {},
    applicationType: [],
    cadastralCode: undefined,
  });
  
  const [activeTab, setActiveTab] = useState('sale');

  const propertyTabs = [
    { id: 'sale', label: t('dealTypes.forSale') },
    { id: 'rent', label: t('dealTypes.forRent') },
    { id: 'mortgage', label: t('dealTypes.leaseholdMortgage') },
    { id: 'daily', label: t('dealTypes.dailyRent') },
    { id: 'new', label: t('dealTypes.newBuildings') },
  ];

  const handleSearch = async () => {
    try {
      const filters: SearchFilters = {
        query: searchForm.query || undefined,
        property_type: searchForm.propertyType === 'all' ? undefined : searchForm.propertyType,
        city: searchForm.location || undefined,
        selectedLocations: searchForm.selectedLocations && searchForm.selectedLocations.length > 0 ? searchForm.selectedLocations : undefined,
        min_rent: searchForm.priceMin,
        max_rent: searchForm.priceMax,
        min_bedrooms: searchForm.bedroomsMin,
        max_bedrooms: searchForm.bedroomsMax,
        // Map other legacy fields for compatibility
        propertyType: searchForm.propertyType === 'all' ? undefined : searchForm.propertyType,
        listingType: activeTab,
        location: searchForm.location || undefined,
        priceMin: searchForm.priceMin,
        priceMax: searchForm.priceMax,
        bedroomsMin: searchForm.bedroomsMin,
        bedroomsMax: searchForm.bedroomsMax,
      };
      
      if (onSearch) {
        // If onSearch prop is provided, use it (for Index page)
        onSearch(filters);
      } else {
        // Otherwise, use the default behavior (navigate to listings)
        await searchProperties(filters);
        navigate('/listings');
      }
      
      addNotification({
        type: 'success',
        title: t('toast.searchCompleted'),
        message: t('toast.searchCompletedMessage'),
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: t('toast.searchFailed'),
        message: t('toast.searchFailedMessage'),
      });
    }
  };

  return (
    <div className={`bg-card shadow-lg rounded-lg overflow-hidden ${className}`}>
      {/* Property Type Tabs */}
      <div className="flex bg-muted/30 border-b border-border">
        {propertyTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search Form */}
      <div className="p-4 space-y-4">
        {/* Main Search Row */}
        <div className="flex gap-3 items-center">
          {/* Property Type Selector */}
          <div className="flex items-center gap-2 min-w-[140px]">
            <Home className="w-4 h-4 text-muted-foreground" />
            <Select 
              value={searchForm.propertyType} 
              onValueChange={(value) => setSearchForm({ ...searchForm, propertyType: value })}
            >
              <SelectTrigger className="border-0 shadow-none bg-transparent">
                <SelectValue placeholder={t('propertyTypes.all')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('propertyTypes.all')}</SelectItem>
                <SelectItem value="apartment">{t('propertyTypes.apartment')}</SelectItem>
                <SelectItem value="house">{t('propertyTypes.house')}</SelectItem>
                <SelectItem value="studio">{t('propertyTypes.studio')}</SelectItem>
                <SelectItem value="commercial">{t('propertyTypes.commercial')}</SelectItem>
                <SelectItem value="land">{t('propertyTypes.land')}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="w-px h-8 bg-border" />

          {/* Location Selector */}
          <LocationSelector
            selectedLocations={searchForm.selectedLocations || []}
            onLocationChange={(locations) => setSearchForm({ ...searchForm, selectedLocations: locations })}
            placeholder={t('search.location')}
            className="min-w-[160px]"
          />

          <div className="w-px h-8 bg-border" />

          {/* Search Input */}
          <div className="flex-1 min-w-[200px]">
            <Input
              type="text"
              placeholder={t('placeholders.phoneIdCadastral')}
              value={searchForm.query}
              onChange={(e) => setSearchForm({ ...searchForm, query: e.target.value })}
              className="border-0 shadow-none bg-transparent focus:ring-0"
            />
          </div>

          {/* Additional Actions */}
          <div className="flex items-center gap-2">
            {/* Advanced Search Dialog */}
            <Dialog>
              <DialogTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8"
                  title="Additional Filters"
                >
                  <SlidersHorizontal className="w-4 h-4" />
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-xl font-semibold text-foreground flex items-center gap-2">
                    {t('search.additionalFilters')}
                  </DialogTitle>
                </DialogHeader>
                
                <div className="space-y-6 py-4">
                  {/* Application Type */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-foreground">{t('labels.applicationType')}</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { key: 'applicationTypes.verified', value: 'Verified' },
                        { key: 'applicationTypes.developerOnly', value: 'Developer only' },
                        { key: 'applicationTypes.withPhotos', value: 'With photos' },
                        { key: 'applicationTypes.onlyByOwner', value: 'Only by the owner' }
                      ].map((type) => (
                        <div key={type.key} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                          <input
                            type="checkbox"
                            id={`simple-app-type-${type.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                          />
                          <label
                            htmlFor={`simple-app-type-${type.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="text-sm font-medium cursor-pointer text-foreground"
                          >
                            {t(type.key)}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Status */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-foreground">{t('common.status')}</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {[
                        { key: 'renovation.notRenovated', value: 'Not renovated' },
                        { key: 'renovation.underRenovation', value: 'Under renovation' },
                        { key: 'renovation.oldRenovated', value: 'Old renovated' },
                        { key: 'renovation.renovated', value: 'Renovated' },
                        { key: 'renovation.newlyRenovated', value: 'Newly renovated' },
                        { key: 'renovation.greenFrame', value: 'Green frame' }
                      ].map((status) => (
                        <div key={status.key} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                          <input
                            type="checkbox"
                            id={`simple-status-${status.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                          />
                          <label
                            htmlFor={`simple-status-${status.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="text-sm font-medium cursor-pointer text-foreground"
                          >
                            {t(status.key)}
                          </label>
                        </div>
                      ))}
                    </div>
                    <div className="grid grid-cols-2 gap-3 mt-3">
                      {[
                        { key: 'renovation.blackFrame', value: 'Black frame' },
                        { key: 'renovation.whiteFrame', value: 'White frame' }
                      ].map((status) => (
                        <div key={status.key} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                          <input
                            type="checkbox"
                            id={`simple-status-${status.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                          />
                          <label
                            htmlFor={`simple-status-${status.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="text-sm font-medium cursor-pointer text-foreground"
                          >
                            {t(status.key)}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Bedrooms and Living Area */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Bedrooms */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium text-foreground">{t('search.bedrooms')}</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <Input 
                          type="number"
                          placeholder={t('placeholders.from')}
                          value={searchForm.bedroomsMin}
                          onChange={(e) => setSearchForm({ ...searchForm, bedroomsMin: Number(e.target.value) })}
                          className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                        />
                        <Input 
                          type="number"
                          placeholder={t('placeholders.to')}
                          value={searchForm.bedroomsMax}
                          onChange={(e) => setSearchForm({ ...searchForm, bedroomsMax: Number(e.target.value) })}
                          className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                        />
                      </div>
                    </div>

                    {/* Living Area */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium text-foreground">{t('search.area')}</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <Input 
                          type="number"
                          placeholder={t('placeholders.fromArea')}
                          value={searchForm.areaMin}
                          onChange={(e) => setSearchForm({ ...searchForm, areaMin: Number(e.target.value) })}
                          className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                        />
                        <Input 
                          type="number"
                          placeholder={t('placeholders.toArea')}
                          value={searchForm.areaMax}
                          onChange={(e) => setSearchForm({ ...searchForm, areaMax: Number(e.target.value) })}
                          className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Yard Area */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-foreground">{t('labels.yardArea')}</h3>
                    <div className="grid grid-cols-2 gap-4 max-w-md">
                      <Input 
                        type="number"
                        placeholder={t('placeholders.fromArea')}
                        value={searchForm.yardAreaMin}
                        onChange={(e) => setSearchForm({ ...searchForm, yardAreaMin: Number(e.target.value) })}
                        className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                      />
                      <Input 
                        type="number"
                        placeholder={t('placeholders.toArea')}
                        value={searchForm.yardAreaMax}
                        onChange={(e) => setSearchForm({ ...searchForm, yardAreaMax: Number(e.target.value) })}
                        className="h-10 border-border focus:border-primary focus:ring-primary text-center"
                      />
                    </div>
                  </div>

                  {/* Additional Information */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-foreground">{t('labels.additionalInformation')}</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {[
                        { key: 'features.centralHeating', value: 'Central heating' },
                        { key: 'features.naturalGas', value: 'Natural gas' },
                        { key: 'features.balcony', value: 'Balcony' },
                        { key: 'features.garage', value: 'Garage' },
                        { key: 'features.storageRoom', value: 'Storage room' },
                        { key: 'features.basement', value: 'Basement' },
                        { key: 'features.drinkingWater', value: 'Drinking water' },
                        { key: 'features.pool', value: 'Pool' },
                        { key: 'features.videoCall', value: 'Video call' }
                      ].map((item) => (
                        <div key={item.key} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all">
                          <input
                            type="checkbox"
                            id={`simple-info-${item.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                          />
                          <label
                            htmlFor={`simple-info-${item.value.toLowerCase().replace(/\s+/g, '-')}`}
                            className="text-sm font-medium cursor-pointer text-foreground"
                          >
                            {t(item.key)}
                          </label>
                        </div>
                      ))}
                    </div>
                    
                    {/* Ukraine Discount - Special styling */}
                    <div className="mt-3">
                      <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-primary/5 transition-all max-w-xs">
                        <input
                          type="checkbox"
                          id="simple-ukraine-discount"
                          className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                        />
                        <label
                          htmlFor="simple-ukraine-discount"
                          className="text-sm font-medium cursor-pointer text-foreground"
                        >
                          🇺🇦 {t('features.ukraineDiscount')}
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Cadastral Code */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-foreground">{t('labels.cadastralCode')}</h3>
                    <Input 
                      placeholder={t('placeholders.enterCadastral')}
                      value={searchForm.cadastralCode}
                      onChange={(e) => setSearchForm({ ...searchForm, cadastralCode: e.target.value })}
                      className="h-10 border-border focus:border-primary focus:ring-primary max-w-md"
                    />
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Find Button */}
          <Button 
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-8"
            onClick={handleSearch}
            disabled={isLoading}
          >
            {isLoading ? t('common.loading') : t('search.find')}
          </Button>
        </div>

        {/* Input Fields Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-border">
          {/* Rooms Range Inputs */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Home className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">{t('labels.rooms')}</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input
                type="number"
                placeholder={t('placeholders.minRooms')}
                value={searchForm.bedroomsMin}
                onChange={(e) => setSearchForm({ ...searchForm, bedroomsMin: Number(e.target.value) })}
                className="h-10 border-border focus:border-primary focus:ring-primary text-center [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
                min="0"
                max="10"
              />
              <Input
                type="number"
                placeholder={t('placeholders.maxRooms')}
                value={searchForm.bedroomsMax}
                onChange={(e) => setSearchForm({ ...searchForm, bedroomsMax: Number(e.target.value) })}
                className="h-10 border-border focus:border-primary focus:ring-primary text-center [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
                min="0"
                max="10"
              />
            </div>
          </div>

          {/* Area Range Inputs */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Building className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">{t('labels.areaRange')}</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input
                type="number"
                placeholder={t('placeholders.minArea')}
                value={searchForm.areaMin}
                onChange={(e) => setSearchForm({ ...searchForm, areaMin: Number(e.target.value) })}
                className="h-10 border-border focus:border-primary focus:ring-primary text-center [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
              />
              <Input
                type="number"
                placeholder={t('placeholders.maxArea')}
                value={searchForm.areaMax}
                onChange={(e) => setSearchForm({ ...searchForm, areaMax: Number(e.target.value) })}
                className="h-10 border-border focus:border-primary focus:ring-primary text-center [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
              />
            </div>
          </div>

          {/* Price Range Inputs */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">{t('search.priceRange')}</span>
              <Select 
                value={searchForm.currency} 
                onValueChange={(value: 'USD' | 'GEL') => setSearchForm({ ...searchForm, currency: value })}
              >
                <SelectTrigger className="w-16 h-6 text-xs border-0 shadow-none bg-transparent">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="usd">USD (₾)</SelectItem>
                  <SelectItem value="gel">GEL (₾)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input
                type="number"
                placeholder={`${t('placeholders.minPrice')} (${searchForm.currency === 'USD' ? '₾' : '₾'})`}
                value={searchForm.priceMin}
                onChange={(e) => setSearchForm({ ...searchForm, priceMin: Number(e.target.value) })}
                className="h-10 border-border focus:border-primary focus:ring-primary text-center [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
              />
              <Input
                type="number"
                placeholder={`${t('placeholders.maxPrice')} (${searchForm.currency === 'USD' ? '₾' : '₾'})`}
                value={searchForm.priceMax}
                onChange={(e) => setSearchForm({ ...searchForm, priceMax: Number(e.target.value) })}
                className="h-10 border-border focus:border-primary focus:ring-primary text-center [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleSearchPanel;
