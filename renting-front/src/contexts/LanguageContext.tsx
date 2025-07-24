import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Language = 'en' | 'geo' | 'rus';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

interface LanguageProviderProps {
  children: ReactNode;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Translation keys and values
const translations = {
  en: {
    // Header
    'header.dashboard': 'Dashboard',
    'header.logout': 'Log Out',
    'header.login': 'Log In',
    'header.publishAd': 'Publish an ad',
    'header.welcome': 'Welcome',
    'header.login': 'Log In',
    'header.publishAd': 'Publish an ad',
    'header.welcome': 'Welcome',
    
    // Dashboard
    'dashboard.title': 'My Dashboard',
    'dashboard.welcome': 'Welcome',
    'dashboard.myListings': 'My Listings',
    'dashboard.saved': 'Saved',
    'dashboard.analytics': 'Analytics',
    'dashboard.settings': 'Settings',
    'dashboard.noListings': 'No listings found.',
    'dashboard.createFirst': 'Start by creating your first property listing!',
    'dashboard.noSaved': 'No saved properties yet.',
    'dashboard.browseSaved': 'Browse properties and save your favorites to see them here.',
    'dashboard.analyticsTitle': 'Analytics Overview',
    'dashboard.totalViews': 'Total Views',
    'dashboard.inquiries': 'Inquiries',
    'dashboard.activeListings': 'Active Listings',
    'dashboard.savedProperties': 'Saved Properties',
    'dashboard.accountSettings': 'Account Settings',
    'dashboard.firstName': 'First Name',
    'dashboard.lastName': 'Last Name',
    'dashboard.email': 'Email',
    'dashboard.phone': 'Phone',
    'dashboard.saveChanges': 'Save Changes',
    'dashboard.enterFirstName': 'Enter your first name',
    'dashboard.enterLastName': 'Enter your last name',
    'dashboard.enterEmail': 'Enter your email',
    'dashboard.enterPhone': 'Enter your phone number',
    'dashboard.views': 'views',
    
    // Common
    'common.active': 'Active',
    'common.inactive': 'Inactive',
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.loginRequired': 'Login Required',
    'common.loginToSave': 'Please log in to save properties',
    'common.propertySaved': 'Property Saved',
    'common.propertyRemoved': 'Property Removed',
    'common.saveFailed': 'Failed to update saved status',
    
    // Toast messages
    'toast.listingDeleted': 'Listing deleted successfully.',
    'toast.deleteError': 'Failed to delete listing. Please try again.',
    'toast.removedFavorites': 'Removed from favorites.',
    'toast.favoritesError': 'Failed to update favorites. Please try again.',
    'toast.profileUpdated': 'Profile updated successfully.',
    'toast.profileError': 'Failed to update profile. Please try again.',
    'toast.dashboardError': 'Failed to load dashboard data. Please try again.',
    'toast.searchCompleted': 'Search completed',
    'toast.searchCompletedMessage': 'Properties loaded successfully.',
    'toast.searchFailed': 'Search failed',
    'toast.searchFailedMessage': 'Unable to search properties. Please try again.',
    
    // Search Panel
    'search.location': 'Location',
    'search.propertyType': 'Property Type',
    'search.priceRange': 'Price Range',
    'search.bedrooms': 'Bedrooms',
    'search.bathrooms': 'Bathrooms',
    'search.find': 'Find',
    'search.advancedFilters': 'Advanced Filters',
    'search.additionalFilters': 'Additional filters',
    'search.area': 'Area (sq m)',
    'search.floor': 'Floor',
    'search.renovationStatus': 'Renovation Status',
    'search.apartment': 'Apartment',
    'search.house': 'House',
    'search.studio': 'Studio',
    'search.commercial': 'Commercial',
    
    // Form Placeholders
    'placeholders.from': 'From',
    'placeholders.to': 'To',
    'placeholders.fromArea': 'From (m²)',
    'placeholders.toArea': 'To (m²)',
    'placeholders.phoneIdCadastral': 'Phone, id, cadastral code',
    'placeholders.enterCadastral': 'Enter cadastral code',
    'placeholders.minRooms': 'Min rooms',
    'placeholders.maxRooms': 'Max rooms',
    'placeholders.minArea': 'Min area',
    'placeholders.maxArea': 'Max area',
    
    // Price Placeholders
    'placeholders.minPrice': 'Min price',
    'placeholders.maxPrice': 'Max price',
    
    // Additional Labels
    'labels.applicationType': 'Application type',
    'labels.yardArea': 'Yard area',
    'labels.additionalInformation': 'Additional information',
    'labels.cadastralCode': 'Cadastral code',
    'labels.rooms': 'Rooms',
    'labels.areaRange': 'Area Range (m²)',
    
    // Application Types
    'applicationTypes.verified': 'Verified',
    'applicationTypes.developerOnly': 'Developer only',
    'applicationTypes.withPhotos': 'With photos',
    'applicationTypes.onlyByOwner': 'Only by the owner',
    
    // Additional Information / Features
    'features.centralHeating': 'Central heating',
    'features.naturalGas': 'Natural gas',
    'features.balcony': 'Balcony',
    'features.garage': 'Garage',
    'features.storageRoom': 'Storage room',
    'features.basement': 'Basement',
    'features.drinkingWater': 'Drinking water',
    'features.pool': 'Pool',
    'features.videoCall': 'Video call',
    'features.ukraineDiscount': 'Discount for citizens of Ukraine',
    
    // Deal Types
    'dealTypes.forSale': 'For sale',
    'dealTypes.forRent': 'For rent',
    'dealTypes.leaseholdMortgage': 'Leasehold Mortgage',
    'dealTypes.dailyRent': 'Daily rent',
    'dealTypes.newBuildings': 'New buildings',
    
    // Property Types
    'propertyTypes.all': 'All types',
    'propertyTypes.apartment': 'Apartment',
    'propertyTypes.house': 'House',
    'propertyTypes.studio': 'Studio',
    'propertyTypes.commercial': 'Commercial',
    'propertyTypes.condo': 'Condo',
    'propertyTypes.townhouse': 'Townhouse',
    'propertyTypes.land': 'Land',
    
    // Common UI Elements
    'common.status': 'Status',
    
    // Renovation Status
    'renovation.notRenovated': 'Not renovated',
    'renovation.underRenovation': 'Under renovation',
    'renovation.oldRenovated': 'Old renovated',
    'renovation.renovated': 'Renovated',
    'renovation.newlyRenovated': 'Newly renovated',
    'renovation.greenFrame': 'Green frame',
    'renovation.blackFrame': 'Black frame',
    'renovation.whiteFrame': 'White frame',
    
    // Ranges
    'ranges.any': 'Any',
    'ranges.studio': 'Studio',
    'ranges.bed1': '1 bedroom',
    'ranges.bed2': '2 bedrooms',
    'ranges.bed3': '3 bedrooms',
    'ranges.bed4': '4+ bedrooms',
    'ranges.bath1': '1 bathroom',
    'ranges.bath2': '2 bathrooms',
    'ranges.bath3': '3+ bathrooms',
    'ranges.priceUp500': 'Up to ₾500',
    'ranges.price500to1000': '$500 - $1,000',
    'ranges.price1000to1500': '$1,000 - $1,500',
    'ranges.price1500to2000': '$1,500 - $2,000',
    'ranges.price2000plus': '$2,000+',
    
    // Listings
    'listings.availableProperties': 'Available Properties',
    'listings.noProperties': 'No properties found matching your criteria.',
    'listings.adjustFilters': 'Try adjusting your search filters.',
    
    // Property Details
    'property.details': 'Property Details',
    'property.description': 'Description',
    'property.features': 'Features',
    'property.location': 'Location',
    'property.contact': 'Contact Information',
    'property.saveProperty': 'Save Property',
    'property.unsaveProperty': 'Remove from Saved',
    'property.gallery': 'Gallery',
    'property.share': 'Share',
    'property.report': 'Report',
    'property.pricePerMonth': 'Price per month',
    'property.deposit': 'Deposit',
    'property.bedrooms': 'Bedrooms',
    'property.bathrooms': 'Bathrooms',
    'property.area': 'Area',
    'property.floor': 'Floor',
    'property.yearBuilt': 'Year Built',
    'property.renovationStatus': 'Renovation Status',
    'property.propertyType': 'Property Type',
    'property.listingType': 'Listing Type',
    'property.dateAdded': 'Date Added',
    'property.contactOwner': 'Contact Owner',
    'property.back': 'Back to Listings',
    
    // Post Ad
    'postAd.title': 'Post Your Property',
    'postAd.propertyDetails': 'Property Details',
    'postAd.propertyTitle': 'Property Title',
    'postAd.description': 'Description',
    'postAd.location': 'Location',
    'postAd.priceAndFeatures': 'Price & Features',
    'postAd.rentAmount': 'Rent Amount',
    'postAd.currency': 'Currency',
    'postAd.deposit': 'Deposit',
    'postAd.propertyType': 'Property Type',
    'postAd.listingType': 'Listing Type',
    'postAd.bedrooms': 'Bedrooms',
    'postAd.bathrooms': 'Bathrooms',
    'postAd.area': 'Area (sq m)',
    'postAd.floor': 'Floor',
    'postAd.renovationStatus': 'Renovation Status',
    'postAd.images': 'Property Images',
    'postAd.uploadImages': 'Upload Images',
    'postAd.publishListing': 'Publish Listing',
    'postAd.publishing': 'Publishing...',
    
    // Footer
    'footer.aboutUs': 'About Us',
    'footer.contactUs': 'Contact Us',
    'footer.privacyPolicy': 'Privacy Policy',
    'footer.cookiePolicy': 'Cookie Policy',
    'footer.termsOfService': 'Terms of Service',
    'footer.allRightsReserved': 'All rights reserved.',
    
    // Auth
    'auth.login': 'Log In',
    'auth.register': 'Register',
    'auth.forgotPassword': 'Forgot Password?',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.confirmPassword': 'Confirm Password',
    'auth.firstName': 'First Name',
    'auth.lastName': 'Last Name',
    'auth.phone': 'Phone',
    'auth.createAccount': 'Create Account',
    'auth.haveAccount': 'Already have an account?',
    'auth.noAccount': "Don't have an account?",
    'auth.signUp': 'Sign up',
    'auth.signIn': 'Sign in',
  },
  
  geo: {
    // Header - Georgian
    'header.dashboard': 'მართვის პანელი',
    'header.logout': 'გასვლა',
    'header.login': 'შესვლა',
    'header.publishAd': 'განცხადების გამოქვეყნება',
    'header.welcome': 'მოგესალმებით',
    
    // Dashboard - Georgian
    'dashboard.title': 'ჩემი მართვის პანელი',
    'dashboard.welcome': 'მოგესალმებით',
    'dashboard.myListings': 'ჩემი განცხადებები',
    'dashboard.saved': 'შენახული',
    'dashboard.analytics': 'ანალიტიკა',
    'dashboard.settings': 'პარამეტრები',
    'dashboard.noListings': 'განცხადებები ვერ მოიძებნა.',
    'dashboard.createFirst': 'დაიწყეთ თქვენი პირველი უძრავი ქონების განცხადების შექმნით!',
    'dashboard.noSaved': 'შენახული უძრავი ქონება ჯერ არ არის.',
    'dashboard.browseSaved': 'დაათვალიერეთ უძრავი ქონება და შეინახეთ თქვენი ფავორიტები აქ სანახავად.',
    'dashboard.analyticsTitle': 'ანალიტიკის მიმოხილვა',
    'dashboard.totalViews': 'სულ ნახვები',
    'dashboard.inquiries': 'მოკითხვები',
    'dashboard.activeListings': 'აქტიური განცხადებები',
    'dashboard.savedProperties': 'შენახული უძრავი ქონება',
    'dashboard.accountSettings': 'ანგარიშის პარამეტრები',
    'dashboard.firstName': 'სახელი',
    'dashboard.lastName': 'გვარი',
    'dashboard.email': 'ელ-ფოსტა',
    'dashboard.phone': 'ტელეფონი',
    'dashboard.saveChanges': 'ცვლილებების შენახვა',
    'dashboard.enterFirstName': 'შეიყვანეთ თქვენი სახელი',
    'dashboard.enterLastName': 'შეიყვანეთ თქვენი გვარი',
    'dashboard.enterEmail': 'შეიყვანეთ თქვენი ელ-ფოსტა',
    'dashboard.enterPhone': 'შეიყვანეთ თქვენი ტელეფონის ნომერი',
    'dashboard.views': 'ნახვები',
    
    // Common - Georgian
    'common.active': 'აქტიური',
    'common.inactive': 'არააქტიური',
    'common.loading': 'იტვირთება...',
    'common.error': 'შეცდომა',
    'common.success': 'წარმატება',
    'common.delete': 'წაშლა',
    'common.edit': 'რედაქტირება',
    'common.save': 'შენახვა',
    'common.cancel': 'გაუქმება',
    'common.loginRequired': 'შესვლა აუცილებელია',
    'common.loginToSave': 'უძრავი ქონების შესანახად გთხოვთ შეხვიდეთ',
    'common.propertySaved': 'უძრავი ქონება შენახულია',
    'common.propertyRemoved': 'უძრავი ქონება ამოღებულია',
    'common.saveFailed': 'შენახული სტატუსის განახლება ვერ მოხერხდა',
    
    // Toast messages - Georgian
    'toast.listingDeleted': 'განცხადება წარმატებით წაიშალა.',
    'toast.deleteError': 'განცხადების წაშლა ვერ მოხერხდა. სცადეთ ხელახლა.',
    'toast.removedFavorites': 'ფავორიტებიდან ამოღებულია.',
    'toast.favoritesError': 'ფავორიტების განახლება ვერ მოხერხდა. სცადეთ ხელახლა.',
    'toast.profileUpdated': 'პროფილი წარმატებით განახლდა.',
    'toast.profileError': 'პროფილის განახლება ვერ მოხერხდა. სცადეთ ხელახლა.',
    'toast.dashboardError': 'მართვის პანელის მონაცემების ჩატვირთვა ვერ მოხერხდა. სცადეთ ხელახლა.',
    'toast.searchCompleted': 'ძებნა დასრულდა',
    'toast.searchCompletedMessage': 'ქონება წარმატებით ჩაიტვირთა.',
    'toast.searchFailed': 'ძებნა ვერ მოხერხდა',
    'toast.searchFailedMessage': 'ქონების ძებნა ვერ მოხერხდა. გთხოვთ სცადოთ ხელახლა.',
    
    // Search Panel - Georgian
    'search.location': 'ადგილმდებარეობა',
    'search.propertyType': 'უძრავი ქონების ტიპი',
    'search.priceRange': 'ფასის დიაპაზონი',
    'search.bedrooms': 'საძინებელი ოთახები',
    'search.bathrooms': 'სააბაზანო ოთახები',
    'search.find': 'ძებნა',
    'search.advancedFilters': 'გაფართოებული ფილტრები',
    'search.additionalFilters': 'დამატებითი ფილტრები',
    'search.area': 'ფართობი (კვ.მ)',
    'search.floor': 'სართული',
    'search.renovationStatus': 'რემონტის სტატუსი',
    'search.apartment': 'ბინა',
    'search.house': 'სახლი',
    'search.studio': 'სტუდია',
    'search.commercial': 'კომერციული',
    
    // Form Placeholders - Georgian
    'placeholders.from': 'დან',
    'placeholders.to': 'მდე',
    'placeholders.fromArea': 'დან (კვ.მ)',
    'placeholders.toArea': 'მდე (კვ.მ)',
    'placeholders.phoneIdCadastral': 'ტელეფონი, ID, კადასტრული კოდი',
    'placeholders.enterCadastral': 'შეიყვანეთ კადასტრული კოდი',
    'placeholders.minRooms': 'მინ ოთახები',
    'placeholders.maxRooms': 'მაქს ოთახები',
    'placeholders.minArea': 'მინ ფართობი',
    'placeholders.maxArea': 'მაქს ფართობი',
    
    // Price Placeholders - Georgian
    'placeholders.minPrice': 'მინ ფასი',
    'placeholders.maxPrice': 'მაქს ფასი',
    
    // Additional Labels - Georgian
    'labels.applicationType': 'განცხადების ტიპი',
    'labels.yardArea': 'ეზოს ფართობი',
    'labels.additionalInformation': 'დამატებითი ინფორმაცია',
    'labels.cadastralCode': 'კადასტრული კოდი',
    'labels.rooms': 'ოთახები',
    'labels.areaRange': 'ფართობის დიაპაზონი (კვ.მ)',
    
    // Application Types - Georgian
    'applicationTypes.verified': 'ვერიფიცირებული',
    'applicationTypes.developerOnly': 'მხოლოდ დეველოპერი',
    'applicationTypes.withPhotos': 'ფოტოებით',
    'applicationTypes.onlyByOwner': 'მხოლოდ მფლობელისგან',
    
    // Additional Information / Features - Georgian
    'features.centralHeating': 'ცენტრალური გათბობა',
    'features.naturalGas': 'ბუნებრივი გაზი',
    'features.balcony': 'აივანი',
    'features.garage': 'გარაჟი',
    'features.storageRoom': 'საცავი',
    'features.basement': 'სარდაფი',
    'features.drinkingWater': 'სასმელი წყალი',
    'features.pool': 'აუზი',
    'features.videoCall': 'ვიდეო ზარი',
    'features.ukraineDiscount': 'ფასდაკლება უკრაინის მოქალაქეებისთვის',
    
    // Deal Types - Georgian
    'dealTypes.forSale': 'გასაყიდად',
    'dealTypes.forRent': 'ქირავდება',
    'dealTypes.leaseholdMortgage': 'იჯარის იპოთეკა',
    'dealTypes.dailyRent': 'დღიური ქირა',
    'dealTypes.newBuildings': 'ახალი შენობები',
    
    // Property Types - Georgian
    'propertyTypes.all': 'ყველა ტიპი',
    'propertyTypes.apartment': 'ბინა',
    'propertyTypes.house': 'სახლი',
    'propertyTypes.studio': 'სტუდია',
    'propertyTypes.commercial': 'კომერციული',
    'propertyTypes.condo': 'კონდომინიუმი',
    'propertyTypes.townhouse': 'ქალაქის სახლი',
    'propertyTypes.land': 'მიწა',
    
    // Common UI Elements - Georgian
    'common.status': 'სტატუსი',
    
    // Renovation Status - Georgian
    'renovation.notRenovated': 'რემონტის გარეშე',
    'renovation.underRenovation': 'რემონტის პროცესში',
    'renovation.oldRenovated': 'ძველი რემონტი',
    'renovation.renovated': 'გარემონტებული',
    'renovation.newlyRenovated': 'ახლად გარემონტებული',
    'renovation.greenFrame': 'მწვანე კარკასი',
    'renovation.blackFrame': 'შავი კარკასი',
    'renovation.whiteFrame': 'თეთრი კარკასი',
    
    // Ranges - Georgian
    'ranges.any': 'ნებისმიერი',
    'ranges.studio': 'სტუდია',
    'ranges.bed1': '1 საძინებელი',
    'ranges.bed2': '2 საძინებელი',
    'ranges.bed3': '3 საძინებელი',
    'ranges.bed4': '4+ საძინებელი',
    'ranges.bath1': '1 სააბაზანო',
    'ranges.bath2': '2 სააბაზანო',
    'ranges.bath3': '3+ სააბაზანო',
    'ranges.priceUp500': '$500-მდე',
    'ranges.price500to1000': '$500 - $1,000',
    'ranges.price1000to1500': '$1,000 - $1,500',
    'ranges.price1500to2000': '$1,500 - $2,000',
    'ranges.price2000plus': '$2,000+',
    'ranges.areaUp50': '50 კვ.მ-მდე',
    'ranges.area50to100': '50 - 100 კვ.მ',
    'ranges.area100to150': '100 - 150 კვ.მ',
    'ranges.area150plus': '150+ კვ.მ',
    
    // Renovation Status - Georgian
    'renovation.notRenovated': 'რემონტის გარეშე',
    'renovation.underRenovation': 'რემონტის პროცესში',
    'renovation.oldRenovated': 'ძველი რემონტი',
    'renovation.renovated': 'გარემონტებული',
    'renovation.newlyRenovated': 'ახლად გარემონტებული',
    'renovation.greenFrame': 'მწვანე კარკასი',
    
    // Listings - Georgian
    'listings.availableProperties': 'ხელმისაწვდომი უძრავი ქონება',
    'listings.noProperties': 'თქვენს კრიტერიუმებთან შესაბამისი უძრავი ქონება ვერ მოიძებნა.',
    'listings.adjustFilters': 'სცადეთ ძიების ფილტრების კორექტირება.',
    
    // Property Details - Georgian
    'property.details': 'უძრავი ქონების დეტალები',
    'property.description': 'აღწერა',
    'property.features': 'მახასიათებლები',
    'property.location': 'ადგილმდებარეობა',
    'property.contact': 'საკონტაქტო ინფორმაცია',
    'property.saveProperty': 'უძრავი ქონების შენახვა',
    'property.unsaveProperty': 'შენახულიდან ამოღება',
    'property.gallery': 'გალერეა',
    'property.share': 'გაზიარება',
    'property.report': 'რეპორტი',
    'property.pricePerMonth': 'ფასი თვეში',
    'property.deposit': 'დეპოზიტი',
    'property.bedrooms': 'საძინებელი ოთახები',
    'property.bathrooms': 'სააბაზანო ოთახები',
    'property.area': 'ფართობი',
    'property.floor': 'სართული',
    'property.yearBuilt': 'აშენების წელი',
    'property.renovationStatus': 'რემონტის სტატუსი',
    'property.propertyType': 'უძრავი ქონების ტიპი',
    'property.listingType': 'განცხადების ტიპი',
    'property.dateAdded': 'დამატების თარიღი',
    'property.contactOwner': 'მფლობელთან კონტაქტი',
    'property.back': 'უკან განცხადებებზე',
    
    // Post Ad - Georgian
    'postAd.title': 'განათავსეთ თქვენი უძრავი ქონება',
    'postAd.propertyDetails': 'უძრავი ქონების დეტალები',
    'postAd.propertyTitle': 'უძრავი ქონების სათაური',
    'postAd.description': 'აღწერა',
    'postAd.location': 'ადგილმდებარეობა',
    'postAd.priceAndFeatures': 'ფასი და მახასიათებლები',
    'postAd.rentAmount': 'ქირის თანხა',
    'postAd.currency': 'ვალუტა',
    'postAd.deposit': 'დეპოზიტი',
    'postAd.propertyType': 'უძრავი ქონების ტიპი',
    'postAd.listingType': 'განცხადების ტიპი',
    'postAd.bedrooms': 'საძინებელი ოთახები',
    'postAd.bathrooms': 'სააბაზანო ოთახები',
    'postAd.area': 'ფართობი (კვ.მ)',
    'postAd.floor': 'სართული',
    'postAd.renovationStatus': 'რემონტის სტატუსი',
    'postAd.images': 'უძრავი ქონების სურათები',
    'postAd.uploadImages': 'სურათების ატვირთვა',
    'postAd.publishListing': 'განცხადების გამოქვეყნება',
    'postAd.publishing': 'გამოქვეყნება...',
    
    // Footer - Georgian
    'footer.aboutUs': 'ჩვენ შესახებ',
    'footer.contactUs': 'დაგვიკავშირდით',
    'footer.privacyPolicy': 'კონფიდენციალურობის პოლიტიკა',
    'footer.cookiePolicy': 'ქუქიების პოლიტიკა',
    'footer.termsOfService': 'მომსახურების პირობები',
    'footer.allRightsReserved': 'ყველა უფლება დაცულია.',
    
    // Auth - Georgian
    'auth.login': 'შესვლა',
    'auth.register': 'რეგისტრაცია',
    'auth.forgotPassword': 'დაგავიწყდათ პაროლი?',
    'auth.email': 'ელ-ფოსტა',
    'auth.password': 'პაროლი',
    'auth.confirmPassword': 'პაროლის დადასტურება',
    'auth.firstName': 'სახელი',
    'auth.lastName': 'გვარი',
    'auth.phone': 'ტელეფონი',
    'auth.createAccount': 'ანგარიშის შექმნა',
    'auth.haveAccount': 'უკვე გაქვთ ანგარიში?',
    'auth.noAccount': 'არ გაქვთ ანგარიში?',
    'auth.signUp': 'რეგისტრაცია',
    'auth.signIn': 'შესვლა',
  },
  
  rus: {
    // Header - Russian
    'header.dashboard': 'Панель управления',
    'header.logout': 'Выйти',
    'header.login': 'Войти',
    'header.publishAd': 'Опубликовать объявление',
    'header.welcome': 'Добро пожаловать',
    
    // Dashboard - Russian
    'dashboard.title': 'Моя панель управления',
    'dashboard.welcome': 'Добро пожаловать',
    'dashboard.myListings': 'Мои объявления',
    'dashboard.saved': 'Сохраненные',
    'dashboard.analytics': 'Аналитика',
    'dashboard.settings': 'Настройки',
    'dashboard.noListings': 'Объявления не найдены.',
    'dashboard.createFirst': 'Начните с создания вашего первого объявления о недвижимости!',
    'dashboard.noSaved': 'Пока нет сохраненной недвижимости.',
    'dashboard.browseSaved': 'Просматривайте недвижимость и сохраняйте ваши избранные, чтобы увидеть их здесь.',
    'dashboard.analyticsTitle': 'Обзор аналитики',
    'dashboard.totalViews': 'Всего просмотров',
    'dashboard.inquiries': 'Запросы',
    'dashboard.activeListings': 'Активные объявления',
    'dashboard.savedProperties': 'Сохраненная недвижимость',
    'dashboard.accountSettings': 'Настройки аккаунта',
    'dashboard.firstName': 'Имя',
    'dashboard.lastName': 'Фамилия',
    'dashboard.email': 'Электронная почта',
    'dashboard.phone': 'Телефон',
    'dashboard.saveChanges': 'Сохранить изменения',
    'dashboard.enterFirstName': 'Введите ваше имя',
    'dashboard.enterLastName': 'Введите вашу фамилию',
    'dashboard.enterEmail': 'Введите ваш email',
    'dashboard.enterPhone': 'Введите ваш номер телефона',
    'dashboard.views': 'просмотров',
    
    // Common - Russian
    'common.active': 'Активный',
    'common.inactive': 'Неактивный',
    'common.loading': 'Загрузка...',
    'common.error': 'Ошибка',
    'common.success': 'Успех',
    'common.delete': 'Удалить',
    'common.edit': 'Редактировать',
    'common.save': 'Сохранить',
    'common.cancel': 'Отмена',
    'common.loginRequired': 'Требуется вход',
    'common.loginToSave': 'Пожалуйста, войдите для сохранения недвижимости',
    'common.propertySaved': 'Недвижимость сохранена',
    'common.propertyRemoved': 'Недвижимость удалена',
    'common.saveFailed': 'Не удалось обновить статус сохранения',
    
    // Toast messages - Russian
    'toast.listingDeleted': 'Объявление успешно удалено.',
    'toast.deleteError': 'Не удалось удалить объявление. Попробуйте еще раз.',
    'toast.removedFavorites': 'Удалено из избранного.',
    'toast.favoritesError': 'Не удалось обновить избранное. Попробуйте еще раз.',
    'toast.profileUpdated': 'Профиль успешно обновлен.',
    'toast.profileError': 'Не удалось обновить профиль. Попробуйте еще раз.',
    'toast.dashboardError': 'Не удалось загрузить данные панели управления. Попробуйте еще раз.',
    'toast.searchCompleted': 'Поиск завершен',
    'toast.searchCompletedMessage': 'Недвижимость успешно загружена.',
    'toast.searchFailed': 'Поиск не удался',
    'toast.searchFailedMessage': 'Не удается найти недвижимость. Пожалуйста, попробуйте еще раз.',
    
    // Search Panel - Russian
    'search.location': 'Расположение',
    'search.propertyType': 'Тип недвижимости',
    'search.priceRange': 'Ценовой диапазон',
    'search.bedrooms': 'Спальни',
    'search.bathrooms': 'Ванные комнаты',
    'search.find': 'Найти',
    'search.advancedFilters': 'Расширенные фильтры',
    'search.additionalFilters': 'Дополнительные фильтры',
    'search.area': 'Площадь (кв.м)',
    'search.floor': 'Этаж',
    'search.renovationStatus': 'Статус ремонта',
    'search.apartment': 'Квартира',
    'search.house': 'Дом',
    'search.studio': 'Студия',
    'search.commercial': 'Коммерческая',
    
    // Form Placeholders - Russian
    'placeholders.from': 'От',
    'placeholders.to': 'До',
    'placeholders.fromArea': 'От (кв.м)',
    'placeholders.toArea': 'До (кв.м)',
    'placeholders.phoneIdCadastral': 'Телефон, ID, кадастровый код',
    'placeholders.enterCadastral': 'Введите кадастровый код',
    'placeholders.minRooms': 'Мин комнаты',
    'placeholders.maxRooms': 'Макс комнаты',
    'placeholders.minArea': 'Мин площадь',
    'placeholders.maxArea': 'Макс площадь',
    
    // Price Placeholders - Russian
    'placeholders.minPrice': 'Мин цена',
    'placeholders.maxPrice': 'Макс цена',
    
    // Additional Labels - Russian
    'labels.applicationType': 'Тип заявки',
    'labels.yardArea': 'Площадь двора',
    'labels.additionalInformation': 'Дополнительная информация',
    'labels.cadastralCode': 'Кадастровый код',
    'labels.rooms': 'Комнаты',
    'labels.areaRange': 'Диапазон площади (кв.м)',
    
    // Application Types - Russian
    'applicationTypes.verified': 'Проверенные',
    'applicationTypes.developerOnly': 'Только застройщик',
    'applicationTypes.withPhotos': 'С фотографиями',
    'applicationTypes.onlyByOwner': 'Только от владельца',
    
    // Additional Information / Features - Russian
    'features.centralHeating': 'Центральное отопление',
    'features.naturalGas': 'Природный газ',
    'features.balcony': 'Балкон',
    'features.garage': 'Гараж',
    'features.storageRoom': 'Кладовая',
    'features.basement': 'Подвал',
    'features.drinkingWater': 'Питьевая вода',
    'features.pool': 'Бассейн',
    'features.videoCall': 'Видеозвонок',
    'features.ukraineDiscount': 'Скидка для граждан Украины',
    
    // Deal Types - Russian
    'dealTypes.forSale': 'Продажа',
    'dealTypes.forRent': 'Аренда',
    'dealTypes.leaseholdMortgage': 'Ипотека аренды',
    'dealTypes.dailyRent': 'Суточная аренда',
    'dealTypes.newBuildings': 'Новостройки',
    
    // Property Types - Russian
    'propertyTypes.all': 'Все типы',
    'propertyTypes.apartment': 'Квартира',
    'propertyTypes.house': 'Дом',
    'propertyTypes.studio': 'Студия',
    'propertyTypes.commercial': 'Коммерческая',
    'propertyTypes.condo': 'Кондоминиум',
    'propertyTypes.townhouse': 'Таунхаус',
    'propertyTypes.land': 'Земля',
    
    // Common UI Elements - Russian
    'common.status': 'Статус',
    
    // Renovation Status - Russian
    'renovation.notRenovated': 'Без ремонта',
    'renovation.underRenovation': 'В процессе ремонта',
    'renovation.oldRenovated': 'Старый ремонт',
    'renovation.renovated': 'Отремонтированная',
    'renovation.newlyRenovated': 'Свежий ремонт',
    'renovation.greenFrame': 'Зеленый каркас',
    'renovation.blackFrame': 'Черный каркас',
    'renovation.whiteFrame': 'Белый каркас',
    
    // Ranges - Russian
    'ranges.any': 'Любой',
    'ranges.studio': 'Студия',
    'ranges.bed1': '1 спальня',
    'ranges.bed2': '2 спальни',
    'ranges.bed3': '3 спальни',
    'ranges.bed4': '4+ спальни',
    'ranges.bath1': '1 ванная',
    'ranges.bath2': '2 ванные',
    'ranges.bath3': '3+ ванные',
    'ranges.priceUp500': 'До $500',
    'ranges.price500to1000': '$500 - $1,000',
    'ranges.price1000to1500': '$1,000 - $1,500',
    'ranges.price1500to2000': '$1,500 - $2,000',
    'ranges.price2000plus': '$2,000+',
    'ranges.areaUp50': 'До 50 кв.м',
    'ranges.area50to100': '50 - 100 кв.м',
    'ranges.area100to150': '100 - 150 кв.м',
    'ranges.area150plus': '150+ кв.м',
    
    // Listings - Russian
    'listings.availableProperties': 'Доступная недвижимость',
    'listings.noProperties': 'Недвижимость, соответствующая вашим критериям, не найдена.',
    'listings.adjustFilters': 'Попробуйте скорректировать фильтры поиска.',
    
    // Property Details - Russian
    'property.details': 'Детали недвижимости',
    'property.description': 'Описание',
    'property.features': 'Характеристики',
    'property.location': 'Расположение',
    'property.contact': 'Контактная информация',
    'property.saveProperty': 'Сохранить недвижимость',
    'property.unsaveProperty': 'Удалить из сохраненных',
    'property.gallery': 'Галерея',
    'property.share': 'Поделиться',
    'property.report': 'Пожаловаться',
    'property.pricePerMonth': 'Цена в месяц',
    'property.deposit': 'Депозит',
    'property.bedrooms': 'Спальни',
    'property.bathrooms': 'Ванные комнаты',
    'property.area': 'Площадь',
    'property.floor': 'Этаж',
    'property.yearBuilt': 'Год постройки',
    'property.renovationStatus': 'Статус ремонта',
    'property.propertyType': 'Тип недвижимости',
    'property.listingType': 'Тип объявления',
    'property.dateAdded': 'Дата добавления',
    'property.contactOwner': 'Связаться с владельцем',
    'property.back': 'Назад к объявлениям',
    
    // Post Ad - Russian
    'postAd.title': 'Разместить вашу недвижимость',
    'postAd.propertyDetails': 'Детали недвижимости',
    'postAd.propertyTitle': 'Название недвижимости',
    'postAd.description': 'Описание',
    'postAd.location': 'Расположение',
    'postAd.priceAndFeatures': 'Цена и характеристики',
    'postAd.rentAmount': 'Сумма аренды',
    'postAd.currency': 'Валюта',
    'postAd.deposit': 'Депозит',
    'postAd.propertyType': 'Тип недвижимости',
    'postAd.listingType': 'Тип объявления',
    'postAd.bedrooms': 'Спальни',
    'postAd.bathrooms': 'Ванные комнаты',
    'postAd.area': 'Площадь (кв.м)',
    'postAd.floor': 'Этаж',
    'postAd.renovationStatus': 'Статус ремонта',
    'postAd.images': 'Фотографии недвижимости',
    'postAd.uploadImages': 'Загрузить фотографии',
    'postAd.publishListing': 'Опубликовать объявление',
    'postAd.publishing': 'Публикация...',
    
    // Footer - Russian
    'footer.aboutUs': 'О нас',
    'footer.contactUs': 'Связаться с нами',
    'footer.privacyPolicy': 'Политика конфиденциальности',
    'footer.cookiePolicy': 'Политика cookies',
    'footer.termsOfService': 'Условия обслуживания',
    'footer.allRightsReserved': 'Все права защищены.',
    
    // Auth - Russian
    'auth.login': 'Войти',
    'auth.register': 'Регистрация',
    'auth.forgotPassword': 'Забыли пароль?',
    'auth.email': 'Email',
    'auth.password': 'Пароль',
    'auth.confirmPassword': 'Подтвердить пароль',
    'auth.firstName': 'Имя',
    'auth.lastName': 'Фамилия',
    'auth.phone': 'Телефон',
    'auth.createAccount': 'Создать аккаунт',
    'auth.haveAccount': 'Уже есть аккаунт?',
    'auth.noAccount': 'Нет аккаунта?',
    'auth.signUp': 'Зарегистрироваться',
    'auth.signIn': 'Войти',
  },
};

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [language, setLanguage] = useState<Language>(() => {
    // Load language from localStorage or default to 'en'
    const savedLanguage = localStorage.getItem('language') as Language;
    return savedLanguage && ['en', 'geo', 'rus'].includes(savedLanguage) ? savedLanguage : 'en';
  });

  // Save language to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  // Translation function
  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  const value = {
    language,
    setLanguage,
    t,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
