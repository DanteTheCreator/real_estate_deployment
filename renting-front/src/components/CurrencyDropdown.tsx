import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { DollarSign, ChevronDown } from 'lucide-react';
import { useCurrency, Currency } from '@/contexts/CurrencyContext';

const currencies = {
  GEL: { code: 'GEL', name: 'Georgian Lari', symbol: '₾', flag: '🇬🇪' },
  USD: { code: 'USD', name: 'US Dollar', symbol: '$', flag: '🇺🇸' },
};

export const CurrencyDropdown: React.FC = () => {
  const { currency, setCurrency } = useCurrency();
  const [isOpen, setIsOpen] = useState(false);

  const handleCurrencyChange = (newCurrency: Currency) => {
    setCurrency(newCurrency);
    setIsOpen(false);
  };

  const currentCurrency = currencies[currency];

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-slate-600 hover:text-blue-600 flex items-center gap-1"
        >
          <DollarSign className="w-4 h-4" />
          <span className="text-sm font-medium">{currentCurrency.code}</span>
          <ChevronDown className="w-3 h-3" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {Object.entries(currencies).map(([currCode, currInfo]) => (
          <DropdownMenuItem
            key={currCode}
            onClick={() => handleCurrencyChange(currCode as Currency)}
            className={`flex items-center gap-3 cursor-pointer ${
              currency === currCode 
                ? 'bg-blue-50 text-blue-600 font-medium' 
                : 'hover:bg-slate-50'
            }`}
          >
            <span className="text-lg">{currInfo.flag}</span>
            <div className="flex flex-col">
              <span className="text-sm font-medium">{currInfo.name}</span>
              <span className="text-xs text-slate-500">{currInfo.symbol} {currInfo.code}</span>
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
