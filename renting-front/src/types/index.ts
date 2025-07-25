// User types - Updated to match your exact FastAPI backend
export interface User {
  id: number; // Your backend uses integer ID
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string; // ISO datetime string
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Property types - Updated to match FastAPI backend
export interface Property {
  id: number; // Backend uses integer ID
  title: string;
  description?: string | null;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country?: string;
  property_type: 'apartment' | 'house' | 'condo' | 'townhouse' | 'studio';
  listing_type: 'rent' | 'sale' | 'lease' | 'daily' | 'mortgage';
  bedrooms: number;
  bathrooms: number;
  square_feet?: number | null;
  lot_size?: number | null;
  rent_amount: number;
  rent_amount_usd?: number | null;
  security_deposit?: number | null;
  lease_duration?: number;
  available_date?: string | null;
  is_furnished?: boolean;
  pets_allowed?: boolean;
  smoking_allowed?: boolean;
  year_built?: number | null;
  parking_spaces?: number;
  utilities_included?: string | null;
  is_available: boolean;
  owner_id?: number;
  created_at: string;
  updated_at?: string | null;
  // Images array to match FastAPI backend structure
  images?: PropertyImage[];
  amenities?: Amenity[];
}

// Legacy interfaces for compatibility (can be removed later)
export interface Address {
  region: string;
  city: string;
  district: string;
  street: string;
  building: string;
  apartment?: string;
  zipCode?: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

// Property Image interface to match FastAPI backend
export interface PropertyImage {
  id: number;
  property_id: number;
  image_url: string;
  caption: string | null;
  is_primary: boolean;
  order_index: number;
  created_at: string;
}

// Amenity interface to match FastAPI backend
export interface Amenity {
  id: number;
  name: string;
  description?: string | null;
  icon?: string | null;
  category?: string | null;
}

export type PropertyStatus = 
  | 'not-renovated' 
  | 'under-renovation' 
  | 'old-renovated' 
  | 'renovated' 
  | 'newly-renovated' 
  | 'green-frame' 
  | 'black-frame' 
  | 'white-frame';

export type PropertyCondition = 'excellent' | 'good' | 'fair' | 'poor';

export interface PropertyFeatures {
  centralHeating: boolean;
  naturalGas: boolean;
  balcony: boolean;
  garage: boolean;
  storageRoom: boolean;
  basement: boolean;
  drinkingWater: boolean;
  pool: boolean;
  videoCall: boolean;
  ukraineDiscount: boolean;
}

export interface PropertyOwner {
  id: string;
  name: string;
  phone: string;
  email?: string;
  isOwner: boolean;
}

export interface PropertyAgent {
  id: string;
  name: string;
  phone: string;
  email: string;
  company: string;
  avatar?: string;
}

// Search and Filter types
export interface SearchFilters {
  query?: string;
  city?: string;
  state?: string;
  property_type?: string;
  min_rent?: number;
  max_rent?: number;
  min_bedrooms?: number;
  max_bedrooms?: number;
  pets_allowed?: boolean;
  is_furnished?: boolean;
  // Legacy fields for compatibility
  propertyType?: string;
  listingType?: string;
  location?: string;
  priceMin?: number;
  priceMax?: number;
  currency?: 'GEL' | 'USD';
  areaMin?: number;
  areaMax?: number;
  bedroomsMin?: number;
  bedroomsMax?: number;
  yardAreaMin?: number;
  yardAreaMax?: number;
  status?: PropertyStatus[];
  features?: Partial<PropertyFeatures>;
  applicationType?: string[];
  cadastralCode?: string;
}

export interface SearchState {
  filters: SearchFilters;
  results: Property[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  sortBy: 'price' | 'area' | 'date' | 'views';
  sortOrder: 'asc' | 'desc';
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    currentPage: number;
    totalPages: number;
    totalCount: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  phone?: string;
  agreeToTerms: boolean;
}

export interface ForgotPasswordForm {
  email: string;
}

export interface ResetPasswordForm {
  token: string;
  password: string;
  confirmPassword: string;
}

export interface PropertyForm {
  title: string;
  description: string;
  price: number;
  currency: 'GEL' | 'USD';
  propertyType: string;
  listingType: string;
  area: number;
  bedrooms?: number;
  bathrooms?: number;
  yardArea?: number;
  floor?: number;
  totalFloors?: number;
  address: Partial<Address>;
  images: File[];
  amenities: string[];
  status: string;
  features: Partial<PropertyFeatures>;
  cadastralCode?: string;
}

// App state types
export interface AppState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  notifications: Notification[];
  favorites: string[];
  recentSearches: SearchFilters[];
  viewMode: 'grid' | 'list';
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// Hook return types
export interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginForm) => Promise<void>;
  register: (data: RegisterForm) => Promise<void>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (data: ResetPasswordForm) => Promise<void>;
  clearError: () => void;
}

export interface UsePropertiesReturn {
  properties: Property[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  searchProperties: (filters: SearchFilters) => Promise<void>;
  loadMore: () => Promise<void>;
  goToPage: (page: number) => Promise<void>;
  refetch: () => Promise<void>;
}

export interface UsePropertyReturn {
  property: Property | null;
  isLoading: boolean;
  error: string | null;
  fetchProperty: (id: string) => Promise<void>;
  updateProperty: (id: string, data: Partial<Property>) => Promise<void>;
  deleteProperty: (id: string) => Promise<void>;
}

export interface UseFavoritesReturn {
  favorites: string[];
  isLoading: boolean;
  error: string | null;
  addToFavorites: (propertyId: string) => Promise<void>;
  removeFromFavorites: (propertyId: string) => Promise<void>;
  isFavorite: (propertyId: string) => boolean;
}

// API endpoints - Updated to match actual FastAPI backend
export const API_ENDPOINTS = {
  // Auth - Matching your actual backend endpoints
  LOGIN: '/auth/login', // POST /api/auth/login
  REGISTER: '/auth/register', // POST /api/auth/register
  LOGOUT: '/auth/logout',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  REFRESH_TOKEN: '/auth/refresh-token',
  VERIFY_EMAIL: '/auth/verify-email',
  CHANGE_PASSWORD: '/auth/change-password', // POST /api/auth/change-password
  
  // Properties - Matching your actual backend
  PROPERTIES: '/properties/', // GET/POST /api/properties/
  PROPERTY_BY_ID: (id: string) => `/properties/${id}`, // /api/properties/{property_id}
  SEARCH_PROPERTIES: '/properties/search', // GET /api/properties/search
  PROPERTIES_COUNT: '/properties/count', // GET /api/properties/count
  SEARCH_PROPERTIES_COUNT: '/properties/search/count', // GET /api/properties/search/count
  FEATURED_PROPERTIES: '/properties/featured',
  MY_PROPERTIES: '/properties/my-properties/', // GET /api/properties/my-properties/
  AMENITIES: '/properties/amenities/', // GET /api/properties/amenities/
  
  // User/Profile - Matching your actual backend
  PROFILE: '/auth/me', // GET/PUT /api/auth/me
  FAVORITES: '/properties/favorites',
  NOTIFICATIONS: '/auth/notifications',
  
  // Applications - Matching your actual backend
  APPLICATIONS: '/applications/', // POST /api/applications/
  APPLICATION_BY_ID: (id: string) => `/applications/${id}`, // GET/DELETE /api/applications/{application_id}
  MY_APPLICATIONS: '/applications/my-applications', // GET /api/applications/my-applications
  PROPERTY_APPLICATIONS: (propertyId: string) => `/applications/property/${propertyId}`, // GET /api/applications/property/{property_id}
  APPLICATION_STATUS: (id: string) => `/applications/${id}/status`, // PUT /api/applications/{application_id}/status
  
  // Upload
  UPLOAD_IMAGE: '/properties/upload-image',
  UPLOAD_IMAGES: '/properties/upload-images',
  
  // MinIO Image endpoints
  MINIO_UPLOAD: '/upload/images',
  MINIO_DELETE: (imagePath: string) => `/upload/images/${imagePath}`,
} as const;
