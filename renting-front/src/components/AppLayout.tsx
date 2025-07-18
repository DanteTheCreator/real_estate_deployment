import React from 'react';
import Header from './Header';
import BannerSlider from './BannerSlider';
import SimpleSearchPanel from './SimpleSearchPanel';
import ListingGrid from './ListingGrid';
import Footer from './Footer';
import { SearchFilters } from '@/types';

interface AppLayoutProps {
  children?: React.ReactNode;
  showBanner?: boolean;
  showSearch?: boolean;
  onSearch?: (filters: SearchFilters) => void;
}

const AppLayout: React.FC<AppLayoutProps> = ({ 
  children, 
  showBanner = false, 
  showSearch = false,
  onSearch 
}) => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main>
        {showBanner && <BannerSlider />}
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {showSearch && <SimpleSearchPanel className="-mt-8 relative z-10" onSearch={onSearch} />}
          
          {children || (
            <>
              <div className="mt-8">
                <ListingGrid />
              </div>
            </>
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export { AppLayout };
export default AppLayout;