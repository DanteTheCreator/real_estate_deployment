import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Plus, User } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { LanguageDropdown } from '@/components/LanguageDropdown';
import { CurrencyDropdown } from '@/components/CurrencyDropdown';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const { t } = useLanguage();

  const handleLoginClick = () => {
    navigate('/auth');
  };

  const handlePostAdClick = () => {
    if (isAuthenticated) {
      navigate('/post-ad');
    } else {
      navigate('/auth');
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
      // Still navigate away even if logout fails
      navigate('/');
    }
  };
  return (
    <header className="bg-white shadow-sm border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div 
              className="cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => navigate('/')}
            >
              <img 
                src="/logo-comfyrent.svg" 
                alt="ComfyRent Logo" 
                className="h-10 w-auto"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-slate-600">
                  {t('header.welcome')}, {user?.first_name}
                </span>
                <Button 
                  variant="ghost" 
                  className="text-slate-600 hover:text-blue-600"
                  onClick={() => navigate('/dashboard')}
                >
                  <User className="w-4 h-4 mr-2" />
                  {t('header.dashboard')}
                </Button>
                <Button 
                  variant="ghost" 
                  className="text-slate-600 hover:text-red-600"
                  onClick={handleLogout}
                >
                  {t('header.logout')}
                </Button>
              </div>
            ) : (
              <Button 
                variant="ghost" 
                className="text-slate-600 hover:text-blue-600"
                onClick={handleLoginClick}
              >
                <User className="w-4 h-4 mr-2" />
                {t('header.login')}
              </Button>
            )}
            
            <CurrencyDropdown />
            <LanguageDropdown />

            <Button 
              className="bg-blue-600 hover:bg-blue-700 text-white"
              onClick={handlePostAdClick}
            >
              <Plus className="w-4 h-4 mr-2" />
              {t('header.publishAd')}
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;