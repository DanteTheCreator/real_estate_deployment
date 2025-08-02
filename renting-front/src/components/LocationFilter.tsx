import React, { useState, useCallback } from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useLanguage } from '@/contexts/LanguageContext';
import { MapPin, ChevronDown, ChevronRight } from 'lucide-react';

export interface LocationItem {
  id: string;
  name: string;
  isParent?: boolean;
  children?: LocationItem[];
}

interface LocationFilterProps {
  locationData: LocationItem[];
  selectedLocations: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  className?: string;
}

export const LocationFilter: React.FC<LocationFilterProps> = ({
  locationData,
  selectedLocations,
  onSelectionChange,
  className = ''
}) => {
  const { t } = useLanguage();
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  // Toggle group expansion
  const toggleGroup = useCallback((groupId: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupId)) {
        newSet.delete(groupId);
      } else {
        newSet.add(groupId);
      }
      return newSet;
    });
  }, []);

  // Get all child IDs for a parent
  const getChildIds = useCallback((parent: LocationItem): string[] => {
    return parent.children?.map(child => child.id) || [];
  }, []);

  // Check if all children are selected
  const areAllChildrenSelected = useCallback((parent: LocationItem): boolean => {
    const childIds = getChildIds(parent);
    return childIds.length > 0 && childIds.every(id => selectedLocations.includes(id));
  }, [selectedLocations, getChildIds]);

  // Check if some (but not all) children are selected
  const areSomeChildrenSelected = useCallback((parent: LocationItem): boolean => {
    const childIds = getChildIds(parent);
    const selectedChildIds = childIds.filter(id => selectedLocations.includes(id));
    return selectedChildIds.length > 0 && selectedChildIds.length < childIds.length;
  }, [selectedLocations, getChildIds]);

  // Handle parent checkbox change
  const handleParentChange = useCallback((parent: LocationItem, checked: boolean) => {
    const childIds = getChildIds(parent);
    let newSelection = [...selectedLocations];

    if (checked) {
      // Select parent and all children
      if (!newSelection.includes(parent.id)) {
        newSelection.push(parent.id);
      }
      childIds.forEach(childId => {
        if (!newSelection.includes(childId)) {
          newSelection.push(childId);
        }
      });
    } else {
      // Deselect parent and all children
      newSelection = newSelection.filter(id => 
        id !== parent.id && !childIds.includes(id)
      );
    }

    onSelectionChange(newSelection);
  }, [selectedLocations, onSelectionChange, getChildIds]);

  // Handle child checkbox change
  const handleChildChange = useCallback((child: LocationItem, parent: LocationItem, checked: boolean) => {
    let newSelection = [...selectedLocations];

    if (checked) {
      // Select child
      if (!newSelection.includes(child.id)) {
        newSelection.push(child.id);
      }
      
      // Check if all children are now selected, if so select parent
      const childIds = getChildIds(parent);
      const selectedChildIds = newSelection.filter(id => childIds.includes(id));
      if (selectedChildIds.length === childIds.length && !newSelection.includes(parent.id)) {
        newSelection.push(parent.id);
      }
    } else {
      // Deselect child
      newSelection = newSelection.filter(id => id !== child.id);
      
      // Deselect parent if it was selected
      newSelection = newSelection.filter(id => id !== parent.id);
    }

    onSelectionChange(newSelection);
  }, [selectedLocations, onSelectionChange, getChildIds]);

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-4 h-4 text-muted-foreground" />
        <h3 className="text-sm font-medium text-foreground">{t('search.location')}</h3>
      </div>
      
      <ScrollArea className="h-[400px] pr-4">
        <div className="space-y-3">
          {locationData.map((parent) => (
            <div key={parent.id} className="space-y-2">
              {/* Parent Item */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleGroup(parent.id)}
                  className="p-1 hover:bg-muted rounded transition-colors"
                  aria-label={`Toggle ${parent.name}`}
                >
                  {expandedGroups.has(parent.id) ? (
                    <ChevronDown className="w-4 h-4 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  )}
                </button>
                
                <div className="flex items-center space-x-2 flex-1">
                  <Checkbox
                    id={`parent-${parent.id}`}
                    checked={areAllChildrenSelected(parent)}
                    ref={(el) => {
                      if (el) {
                        el.indeterminate = areSomeChildrenSelected(parent);
                      }
                    }}
                    onCheckedChange={(checked) => handleParentChange(parent, checked as boolean)}
                    className="data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                  />
                  <label
                    htmlFor={`parent-${parent.id}`}
                    className="text-sm font-semibold text-foreground cursor-pointer select-none"
                  >
                    {parent.name}
                  </label>
                </div>
              </div>

              {/* Children Items */}
              {expandedGroups.has(parent.id) && parent.children && (
                <div className="ml-8 space-y-2 border-l-2 border-muted pl-4">
                  {parent.children.map((child) => (
                    <div key={child.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`child-${child.id}`}
                        checked={selectedLocations.includes(child.id)}
                        onCheckedChange={(checked) => handleChildChange(child, parent, checked as boolean)}
                        className="data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                      />
                      <label
                        htmlFor={`child-${child.id}`}
                        className="text-sm text-muted-foreground cursor-pointer select-none hover:text-primary transition-colors"
                      >
                        {child.name}
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};

// Location data for Tbilisi neighborhoods
export const tbilisiLocationData: LocationItem[] = [
  {
    id: 'vake-saburtalo',
    name: 'ვაკე-საბურთალო',
    isParent: true,
    children: [
      { id: 'vake', name: 'ვაკე' },
      { id: 'saburtalo', name: 'საბურთალო' },
      { id: 'digomi', name: 'დიღომი' },
      { id: 'ponichala', name: 'ფონიჩალა' },
      { id: 'kus-tba', name: 'კუს ტბა' },
      { id: 'temqa', name: 'ლისი ტემქა' },
      { id: 'digmis-chala', name: 'დიღმის ჩალა' },
      { id: 'davit-aghmasheneblis-gamz', name: 'დავით აღმაშენებლის გამზ.' }
    ]
  },
  {
    id: 'isani-samgori',
    name: 'ისანი-სამგორი',
    isParent: true,
    children: [
      { id: 'avtomsheneblis-dal', name: 'ავტომშენებლის დალ.' },
      { id: 'damtsklis-dal', name: 'დამასკლის დალ.' },
      { id: 'varketilis-dal', name: 'ვარკეთილს დალ.' },
      { id: 'navtlughi', name: 'ნავთლუღი' },
      { id: 'varchkhotili', name: 'ვარჩხოთილი' },
      { id: 'orchevi', name: 'ორჩევი' },
      { id: 'nachikebi', name: 'ნაჩიკები' },
      { id: 'samgori', name: 'სამგორი' }
    ]
  },
  {
    id: 'gldani-nadzaladevi',
    name: 'გლდანი-ნაძალადევი',
    isParent: true,
    children: [
      { id: 'gldani', name: 'გლდანი' },
      { id: 'gldanula', name: 'გლდანულა' },
      { id: 'baghebi', name: 'ბაღები' },
      { id: 'othkhlis-bdo', name: 'ოთხოლის ბდო' },
      { id: 'telqa', name: 'თელქა' },
      { id: 'korchanki-dal', name: 'კორჩანკის დალ.' },
      { id: 'lilo', name: 'ლილო' },
      { id: 'sof-gldan', name: 'სოფ. გლდან' },
      { id: 'avchala', name: 'ავჩალა' },
      { id: 'gioni-grmebi-dal', name: 'გიორგი გრმების დალ.' }
    ]
  },
  {
    id: 'didube-chughureti',
    name: 'დიდუბე-ჩუღურეთი',
    isParent: true,
    children: [
      { id: 'didube', name: 'დიდუბე' },
      { id: 'didubis-masivi', name: 'დიდუბის მასივი' },
      { id: 'kuki', name: 'კუკია' },
      { id: 'chrdilis', name: 'ჩრდილის' },
      { id: 'teleti', name: 'თელეთი' },
      { id: 'iveritubani', name: 'ივერიუბანი' },
      { id: 'avlabari', name: 'ავლაბარი' },
      { id: 'tseretlis-dal', name: 'წერეთლის დალ.' },
      { id: 'mukhatgverdi', name: 'მუხათგვერდი' }
    ]
  },
  {
    id: 'old-tbilisi',
    name: 'ძველი თბილისი',
    isParent: true,
    children: [
      { id: 'abanotubani', name: 'აბანოთუბანი' },
      { id: 'ananuri-gverdi', name: 'ანანურის გვერდი' },
      { id: 'aglabari', name: 'ავლაბარი' },
      { id: 'elia', name: 'ელია' },
      { id: 'metekhi', name: 'მეტეხი' },
      { id: 'sameba', name: 'სამება' },
      { id: 'sololaki', name: 'სოლოლაკი' }
    ]
  },
  {
    id: 'tbilisis-shemogvarea',
    name: 'თბილისის შემოგვარეა...',
    isParent: true,
    children: [
      { id: 'tskhinvali', name: 'ცხინვალი' },
      { id: 'abokhaleba', name: 'აბოხალება' },
      { id: 'botaniki', name: 'ბოტანიკი' },
      { id: 'kaklebi', name: 'კაკლები' },
      { id: 'kotkhebi', name: 'კოტხები' },
      { id: 'ortachala', name: 'ორთაჩალა' },
      { id: 'shindisi', name: 'შინდისი' },
      { id: 'tsavkisi', name: 'წავკისი' },
      { id: 'tskneti', name: 'წყნეთი' },
      { id: 'meshakhte', name: 'მესხეთე' },
      { id: 'akhaldaba', name: 'ახალდაბა' },
      { id: 'mtskheta', name: 'მცხეთა' },
      { id: 'begiti', name: 'ბეგითი' },
      { id: 'kweseti', name: 'კვესეთი' }
    ]
  }
];
