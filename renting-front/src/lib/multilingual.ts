import { Property, Amenity } from '@/types';
import { Language } from '@/contexts/LanguageContext';

/**
 * Get localized title for a property based on current language
 */
export function getLocalizedTitle(property: Property, language: Language): string {
  switch (language) {
    case 'en':
      return property.title_en || property.title;
    case 'rus':
      return property.title_ru || property.title;
    case 'geo':
    default:
      return property.title;
  }
}

/**
 * Get localized description for a property based on current language
 */
export function getLocalizedDescription(property: Property, language: Language): string | null {
  switch (language) {
    case 'en':
      return property.description_en || property.description || null;
    case 'rus':
      return property.description_ru || property.description || null;
    case 'geo':
    default:
      return property.description || null;
  }
}

/**
 * Get localized name for an amenity based on current language
 */
export function getLocalizedAmenityName(amenity: Amenity, language: Language): string {
  switch (language) {
    case 'en':
      return amenity.name_en || amenity.name;
    case 'rus':
      return amenity.name_ru || amenity.name;
    case 'geo':
    default:
      return amenity.name;
  }
}

/**
 * Get localized description for an amenity based on current language
 */
export function getLocalizedAmenityDescription(amenity: Amenity, language: Language): string | null {
  switch (language) {
    case 'en':
      return amenity.description_en || amenity.description || null;
    case 'rus':
      return amenity.description_ru || amenity.description || null;
    case 'geo':
    default:
      return amenity.description || null;
  }
}

/**
 * Create a localized property object with the correct title and description for the current language
 */
export function getLocalizedProperty(property: Property, language: Language): Property {
  return {
    ...property,
    title: getLocalizedTitle(property, language),
    description: getLocalizedDescription(property, language),
    amenities: property.amenities?.map(amenity => ({
      ...amenity,
      name: getLocalizedAmenityName(amenity, language),
      description: getLocalizedAmenityDescription(amenity, language)
    }))
  };
}
