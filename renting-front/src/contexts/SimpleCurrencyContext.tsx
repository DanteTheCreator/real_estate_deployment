import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Currency = 'USD' | 'GEL';

interface SimpleCurrencyContextType {
  currency: Currency;
  setCurrency: (currency: Currency) => void;
  formatPrice: (gelAmount: number, usdAmount?: number | null, listingType?: string) => string;
}

const SimpleCurrencyContext = createContext<SimpleCurrencyContextType | undefined>(undefined);

interface SimpleCurrencyProviderProps {
  children: ReactNode;
}

export const SimpleCurrencyProvider: React.FC<SimpleCurrencyProviderProps> = ({ children }) => {
  const [currency, setCurrencyState] = useState<Currency>('GEL');

  // Load currency from localStorage on mount
  useEffect(() => {
    const storedCurrency = localStorage.getItem('comfyrent_currency') as Currency;
    if (storedCurrency === 'USD' || storedCurrency === 'GEL') {
      setCurrencyState(storedCurrency);
    }
  }, []);

  // Save currency to localStorage when it changes
  const setCurrency = (newCurrency: Currency) => {
    setCurrencyState(newCurrency);
    localStorage.setItem('comfyrent_currency', newCurrency);
  };

  // Format price based on current currency
  const formatPrice = (gelAmount: number, usdAmount?: number | null, listingType?: string): string => {
    // Determine which amount to use
    let amount = gelAmount;
    let symbol = '₾';
    
    if (currency === 'USD' && usdAmount) {
      amount = usdAmount;
      symbol = '$';
    }
    
    const formattedAmount = `${symbol}${amount.toLocaleString()}`;
    
    // Only add "/month" for rental properties, NOT for sale properties
    if (listingType === 'sale') {
      return formattedAmount;
    } else {
      return `${formattedAmount}/month`;
    }
  };

  const value: SimpleCurrencyContextType = {
    currency,
    setCurrency,
    formatPrice,
  };

  return (
    <SimpleCurrencyContext.Provider value={value}>
      {children}
    </SimpleCurrencyContext.Provider>
  );
};

export const useSimpleCurrency = (): SimpleCurrencyContextType => {
  const context = useContext(SimpleCurrencyContext);
  if (context === undefined) {
    throw new Error('useSimpleCurrency must be used within a SimpleCurrencyProvider');
  }
  return context;
};
