import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { LocationFilter, tbilisiLocationData, LocationItem } from './LocationFilter';
import { useLanguage } from '@/contexts/LanguageContext';
import { MapPin, X } from 'lucide-react';

interface LocationSelectorProps {
  selectedLocations: string[];
  onLocationChange: (locations: string[]) => void;
  placeholder?: string;
  className?: string;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({
  selectedLocations,
  onLocationChange,
  placeholder,
  className = ''
}) => {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [tempSelection, setTempSelection] = useState<string[]>(selectedLocations);

  // Use language context for placeholder if not provided
  const displayPlaceholder = placeholder || t('common.selectLocation');

  // Get display text for selected locations
  const getDisplayText = () => {
    if (selectedLocations.length === 0) {
      return displayPlaceholder;
    }

    // Get all location items (including children) for name lookup
    const allLocations = new Map<string, string>();
    tbilisiLocationData.forEach(parent => {
      allLocations.set(parent.id, parent.name);
      parent.children?.forEach(child => {
        allLocations.set(child.id, child.name);
      });
    });

    const selectedNames = selectedLocations
      .map(id => allLocations.get(id))
      .filter(Boolean)
      .slice(0, 3); // Show max 3 names

    if (selectedLocations.length > 3) {
      return `${selectedNames.join(', ')} +${selectedLocations.length - 3}`;
    }

    return selectedNames.join(', ');
  };

  const handleOpenChange = (open: boolean) => {
    if (open) {
      setTempSelection(selectedLocations);
    }
    setIsOpen(open);
  };

  const handleApply = () => {
    onLocationChange(tempSelection);
    setIsOpen(false);
  };

  const handleCancel = () => {
    setTempSelection(selectedLocations);
    setIsOpen(false);
  };

  const handleClear = () => {
    setTempSelection([]);
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <div className={`flex items-center gap-2 min-w-[160px] ${className}`}>
          <MapPin className="w-4 h-4 text-muted-foreground" />
          <Button
            variant="ghost"
            className={`border-0 shadow-none bg-transparent justify-start p-0 h-auto font-normal ${
              selectedLocations.length > 0 ? 'text-foreground' : 'text-muted-foreground'
            }`}
          >
            <span className="truncate">{getDisplayText()}</span>
          </Button>
        </div>
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-foreground flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            {t('common.selectLocation')}
          </DialogTitle>
        </DialogHeader>
        
        <div className="flex-1 overflow-hidden">
          <LocationFilter
            locationData={tbilisiLocationData}
            selectedLocations={tempSelection}
            onSelectionChange={setTempSelection}
          />
        </div>
        
        <DialogFooter className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {tempSelection.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4 mr-1" />
                {t('common.clear')}
              </Button>
            )}
            {tempSelection.length > 0 && (
              <span className="text-xs text-muted-foreground">
                {t('common.selected')}: {tempSelection.length}
              </span>
            )}
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleCancel}>
              {t('common.cancel')}
            </Button>
            <Button size="sm" onClick={handleApply}>
              {t('common.confirm')}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
