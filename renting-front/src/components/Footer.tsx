import React from 'react';
import { Link } from 'react-router-dom';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { Facebook, Twitter, Instagram, Phone, Mail } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

const Footer: React.FC = () => {
  const { t } = useLanguage();
  
  return (
    <footer className="bg-muted border-t mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="mb-4">
              <img 
                src="/logo-comfyrent.svg" 
                alt="ComfyRent Logo" 
                className="h-8 w-auto"
              />
            </div>
            <p className="text-muted-foreground text-sm mb-4">
              Experience stress-free property searching with our modern platform. One listing per property guaranteed - because your time matters.
            </p>
            <div className="flex space-x-3">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Facebook className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Twitter className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Instagram className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4 text-foreground">Help</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a 
                  href="tel:+995599738023" 
                  className="text-muted-foreground hover:text-primary transition-colors cursor-pointer"
                >
                  FAQ
                </a>
              </li>
              <li>
                <a 
                  href="tel:+995599738023" 
                  className="text-muted-foreground hover:text-primary transition-colors cursor-pointer"
                >
                  Contact
                </a>
              </li>
              <li>
                <a 
                  href="tel:+995599738023" 
                  className="text-muted-foreground hover:text-primary transition-colors cursor-pointer"
                >
                  Support
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4 text-foreground">{t('footer.contactUs')}</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <a 
                  href="tel:+995599738023" 
                  className="text-muted-foreground hover:text-primary transition-colors cursor-pointer"
                >
                  + 995599738023
                </a>
              </div>
              <div className="flex items-center space-x-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <a 
                  href="mailto:info.nextep.solutions@gmail.com" 
                  className="text-muted-foreground hover:text-primary transition-colors cursor-pointer"
                >
                  info.nextep.solutions@gmail.com
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <Separator className="my-8" />
        
        <div className="flex flex-col md:flex-row justify-between items-center text-sm text-muted-foreground">
          <div className="flex space-x-6 mb-4 md:mb-0">
            <Link to="/privacy-policy" className="hover:text-primary">{t('footer.privacyPolicy')}</Link>
            <Link to="/terms-of-service" className="hover:text-primary">{t('footer.termsOfService')}</Link>
            <Link to="/cookie-policy" className="hover:text-primary">{t('footer.cookiePolicy')}</Link>
          </div>
          <div>
            © 2024 ComfyRent. {t('footer.allRightsReserved')}
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;