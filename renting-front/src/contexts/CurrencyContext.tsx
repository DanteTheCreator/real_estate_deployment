import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Currency = 'USD' | 'GEL';

interface CurrencyContextType {
  currency: Currency;
  setCurrency: (currency: Currency) => void;
  formatPrice: (gelAmount: number, usdAmount?: number | null, listingType?: string) => string;
  getCurrencySymbol: () => string;
  getAmount: (gelAmount: number, usdAmount?: number | null) => number;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

interface CurrencyProviderProps {
  children: ReactNode;
}

export const CurrencyProvider: React.FC<CurrencyProviderProps> = ({ children }) => {
  const [currency, setCurrencyState] = useState<Currency>('GEL');

  // Load currency from localStorage on mount
  useEffect(() => {
    const storedCurrency = localStorage.getItem('comfyrent_currency') as Currency;
    if (storedCurrency && (storedCurrency === 'USD' || storedCurrency === 'GEL')) {
      setCurrencyState(storedCurrency);
    }
  }, []);

  // Save currency to localStorage when it changes
  const setCurrency = (newCurrency: Currency) => {
    console.log('Currency changing from', currency, 'to', newCurrency);
    setCurrencyState(newCurrency);
    localStorage.setItem('comfyrent_currency', newCurrency);
  };

  // Get the appropriate amount based on current currency
  const getAmount = (gelAmount: number, usdAmount?: number | null): number => {
    if (currency === 'USD' && usdAmount !== null && usdAmount !== undefined) {
      return usdAmount;
    }
    return gelAmount; // Default to GEL amount
  };

  // Format price based on current currency
  const formatPrice = (gelAmount: number, usdAmount?: number | null, listingType?: string): string => {
    const amount = getAmount(gelAmount, usdAmount);
    const formattedAmount = currency === 'USD' ? `$${amount.toLocaleString()}` : `₾${amount.toLocaleString()}`;
    
    // Temporary debug logging
    console.log('Currency debug:', { currency, gelAmount, usdAmount, selectedAmount: amount, result: formattedAmount });
    
    // Remove "per month" suffix as requested - show only the formatted amount
    return formattedAmount;
  };

  // Get currency symbol
  const getCurrencySymbol = (): string => {
    return currency === 'USD' ? '$' : '₾';
  };

  const value: CurrencyContextType = {
    currency,
    setCurrency,
    formatPrice,
    getCurrencySymbol,
    getAmount,
  };

  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = (): CurrencyContextType => {
  const context = useContext(CurrencyContext);
  if (context === undefined) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};
