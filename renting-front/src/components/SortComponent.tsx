import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

export interface SortOptions {
  sortBy: 'price' | 'area' | 'date' | 'bedrooms';
  sortOrder: 'asc' | 'desc';
}

interface SortComponentProps {
  sortBy: string;
  sortOrder: string;
  onSortChange: (sortBy: string, sortOrder: string) => void;
  className?: string;
  compact?: boolean;
}

export const SortComponent: React.FC<SortComponentProps> = ({
  sortBy,
  sortOrder,
  onSortChange,
  className = '',
  compact = false
}) => {
  const sortOptions = [
    { value: 'date', label: 'Date Added', icon: '📅' },
    { value: 'price', label: 'Price', icon: '💰' },
    { value: 'area', label: 'Area (m²)', icon: '📐' },
    { value: 'bedrooms', label: 'Bedrooms', icon: '🛏️' },
  ];

  const toggleSortOrder = () => {
    const newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    onSortChange(sortBy, newOrder);
  };

  const handleSortByChange = (newSortBy: string) => {
    onSortChange(newSortBy, sortOrder);
  };

  if (compact) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Select value={sortBy} onValueChange={handleSortByChange}>
          <SelectTrigger className="w-[140px] h-9 text-sm">
            <SelectValue placeholder="Sort by..." />
          </SelectTrigger>
          <SelectContent>
            {sortOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                <div className="flex items-center gap-2">
                  <span>{option.icon}</span>
                  <span>{option.label}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        <Button
          variant="outline"
          size="sm"
          onClick={toggleSortOrder}
          className="h-9 w-9 p-0"
          title={`Sort ${sortOrder === 'asc' ? 'ascending' : 'descending'}`}
        >
          {sortOrder === 'asc' ? (
            <ArrowUp className="h-4 w-4" />
          ) : (
            <ArrowDown className="h-4 w-4" />
          )}
        </Button>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center gap-2 text-sm font-medium text-foreground">
        <ArrowUpDown className="w-4 h-4" />
        Sort Results
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Sort By Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">Sort by</label>
          <Select value={sortBy} onValueChange={handleSortByChange}>
            <SelectTrigger className="h-11 border-border focus:border-primary focus:ring-primary">
              <SelectValue placeholder="Choose sort criteria" />
            </SelectTrigger>
            <SelectContent>
              {sortOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex items-center gap-2">
                    <span>{option.icon}</span>
                    <span>{option.label}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Sort Order Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">Order</label>
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant={sortOrder === 'desc' ? 'default' : 'outline'}
              onClick={() => onSortChange(sortBy, 'desc')}
              className="h-11 flex items-center gap-2 justify-center"
            >
              <ArrowDown className="w-4 h-4" />
              <span className="hidden sm:inline">
                {sortBy === 'price' ? 'High to Low' : 
                 sortBy === 'area' ? 'Large to Small' : 
                 sortBy === 'date' ? 'Newest First' : 
                 'Most to Least'}
              </span>
              <span className="sm:hidden">
                {sortBy === 'price' ? 'High-Low' : 
                 sortBy === 'area' ? 'Large-Small' : 
                 sortBy === 'date' ? 'Newest' : 
                 'Most'}
              </span>
            </Button>
            <Button
              variant={sortOrder === 'asc' ? 'default' : 'outline'}
              onClick={() => onSortChange(sortBy, 'asc')}
              className="h-11 flex items-center gap-2 justify-center"
            >
              <ArrowUp className="w-4 h-4" />
              <span className="hidden sm:inline">
                {sortBy === 'price' ? 'Low to High' : 
                 sortBy === 'area' ? 'Small to Large' : 
                 sortBy === 'date' ? 'Oldest First' : 
                 'Least to Most'}
              </span>
              <span className="sm:hidden">
                {sortBy === 'price' ? 'Low-High' : 
                 sortBy === 'area' ? 'Small-Large' : 
                 sortBy === 'date' ? 'Oldest' : 
                 'Least'}
              </span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
