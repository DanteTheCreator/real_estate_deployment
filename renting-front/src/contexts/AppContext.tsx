import React, { createContext, useContext, useState, useEffect } from 'react';
import { AppState, Notification, SearchFilters } from '@/types';
import { toast } from '@/components/ui/use-toast';

interface AppContextType extends AppState {
  // Theme
  toggleTheme: () => void;
  
  // Sidebar
  toggleSidebar: () => void;
  closeSidebar: () => void;
  
  // Notifications
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationAsRead: (id: string) => void;
  clearNotifications: () => void;
  unreadCount: number;
  
  // Favorites
  toggleFavorite: (propertyId: string) => void;
  isFavorite: (propertyId: string) => boolean;
  
  // Recent searches
  addRecentSearch: (search: SearchFilters) => void;
  clearRecentSearches: () => void;
  
  // View mode
  toggleViewMode: () => void;
  setViewMode: (mode: 'grid' | 'list') => void;
}

const defaultAppState: AppState = {
  theme: 'light',
  sidebarOpen: false,
  notifications: [],
  favorites: [],
  recentSearches: [],
  viewMode: 'grid',
};

const defaultAppContext: AppContextType = {
  ...defaultAppState,
  toggleTheme: () => {},
  toggleSidebar: () => {},
  closeSidebar: () => {},
  addNotification: () => {},
  markNotificationAsRead: () => {},
  clearNotifications: () => {},
  unreadCount: 0,
  toggleFavorite: () => {},
  isFavorite: () => false,
  addRecentSearch: () => {},
  clearRecentSearches: () => {},
  toggleViewMode: () => {},
  setViewMode: () => {},
};

const AppContext = createContext<AppContextType>(defaultAppContext);

export const useAppContext = () => useContext(AppContext);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppState>(() => {
    // Load state from localStorage on initialization
    const saved = localStorage.getItem('comfyrent-app-state');
    if (saved) {
      try {
        return { ...defaultAppState, ...JSON.parse(saved) };
      } catch (error) {
        console.error('Failed to parse saved app state:', error);
      }
    }
    return defaultAppState;
  });

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('comfyrent-app-state', JSON.stringify(state));
  }, [state]);

  const toggleTheme = () => {
    setState(prev => ({
      ...prev,
      theme: prev.theme === 'light' ? 'dark' : 'light'
    }));
  };

  const toggleSidebar = () => {
    setState(prev => ({
      ...prev,
      sidebarOpen: !prev.sidebarOpen
    }));
  };

  const closeSidebar = () => {
    setState(prev => ({
      ...prev,
      sidebarOpen: false
    }));
  };

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      read: false,
    };

    setState(prev => ({
      ...prev,
      notifications: [newNotification, ...prev.notifications].slice(0, 50) // Keep only last 50
    }));

    // Show toast notification
    toast({
      title: notification.title,
      description: notification.message,
      variant: notification.type === 'error' ? 'destructive' : 'default',
    });
  };

  const markNotificationAsRead = (id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    }));
  };

  const clearNotifications = () => {
    setState(prev => ({
      ...prev,
      notifications: []
    }));
  };

  const toggleFavorite = (propertyId: string) => {
    setState(prev => ({
      ...prev,
      favorites: prev.favorites.includes(propertyId)
        ? prev.favorites.filter(id => id !== propertyId)
        : [...prev.favorites, propertyId]
    }));
  };

  const isFavorite = (propertyId: string) => {
    return state.favorites.includes(propertyId);
  };

  const addRecentSearch = (search: SearchFilters) => {
    setState(prev => ({
      ...prev,
      recentSearches: [
        search,
        ...prev.recentSearches.filter(s => JSON.stringify(s) !== JSON.stringify(search))
      ].slice(0, 10) // Keep only last 10 searches
    }));
  };

  const clearRecentSearches = () => {
    setState(prev => ({
      ...prev,
      recentSearches: []
    }));
  };

  const toggleViewMode = () => {
    setState(prev => ({
      ...prev,
      viewMode: prev.viewMode === 'grid' ? 'list' : 'grid'
    }));
  };

  const setViewMode = (mode: 'grid' | 'list') => {
    setState(prev => ({
      ...prev,
      viewMode: mode
    }));
  };

  const unreadCount = state.notifications.filter(n => !n.read).length;

  const contextValue: AppContextType = {
    ...state,
    toggleTheme,
    toggleSidebar,
    closeSidebar,
    addNotification,
    markNotificationAsRead,
    clearNotifications,
    unreadCount,
    toggleFavorite,
    isFavorite,
    addRecentSearch,
    clearRecentSearches,
    toggleViewMode,
    setViewMode,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};
