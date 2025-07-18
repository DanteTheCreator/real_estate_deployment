import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Globe, ChevronDown } from 'lucide-react';
import { useLanguage, Language } from '@/contexts/LanguageContext';

const languages = {
  en: { code: 'EN', name: 'English', flag: '🇺🇸' },
  geo: { code: 'GEO', name: 'ქართული', flag: '🇬🇪' },
  rus: { code: 'RUS', name: 'Русский', flag: '🇷🇺' },
};

export const LanguageDropdown: React.FC = () => {
  const { language, setLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    setIsOpen(false);
  };

  const currentLanguage = languages[language];

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-slate-600 hover:text-blue-600 flex items-center gap-1"
        >
          <Globe className="w-4 h-4" />
          <span className="text-sm font-medium">{currentLanguage.code}</span>
          <ChevronDown className="w-3 h-3" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {Object.entries(languages).map(([langCode, langInfo]) => (
          <DropdownMenuItem
            key={langCode}
            onClick={() => handleLanguageChange(langCode as Language)}
            className={`flex items-center gap-3 cursor-pointer ${
              language === langCode 
                ? 'bg-blue-50 text-blue-600 font-medium' 
                : 'hover:bg-slate-50'
            }`}
          >
            <span className="text-lg">{langInfo.flag}</span>
            <div className="flex flex-col">
              <span className="text-sm font-medium">{langInfo.name}</span>
              <span className="text-xs text-slate-500">{langInfo.code}</span>
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
