import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthState, LoginForm, RegisterForm, ResetPasswordForm, UseAuthReturn } from '@/types';
import { authService } from '@/services';

const defaultAuthState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

const AuthContext = createContext<UseAuthReturn | null>(null);

export const useAuth = (): UseAuthReturn => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    // Initialize from localStorage
    const savedToken = localStorage.getItem('comfyrent-token');
    const savedUser = localStorage.getItem('comfyrent-user');
    
    if (savedToken && savedUser) {
      try {
        return {
          user: JSON.parse(savedUser),
          token: savedToken,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        };
      } catch (error) {
        console.error('Failed to parse saved auth data:', error);
        localStorage.removeItem('comfyrent-token');
        localStorage.removeItem('comfyrent-user');
      }
    }
    
    return defaultAuthState;
  });

  // Auto-refresh token on app start if user is logged in
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('comfyrent-token');
      const savedUser = localStorage.getItem('comfyrent-user');
      
      if (savedToken && savedUser) {
        setAuthState(prev => ({ ...prev, isLoading: true }));
        try {
          const response = await authService.refreshToken();
          setAuthState({
            user: response.user,
            token: response.token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          localStorage.setItem('comfyrent-token', response.token);
          localStorage.setItem('comfyrent-user', JSON.stringify(response.user));
        } catch (error) {
          console.error('Token refresh failed:', error);
          // Clear invalid token
          localStorage.removeItem('comfyrent-token');
          localStorage.removeItem('comfyrent-user');
          setAuthState(defaultAuthState);
        }
      }
    };

    // Only run on component mount
    initAuth();
  }, []); // Empty dependency array is intentional - only run on mount

  const login = async (credentials: LoginForm): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await authService.login(credentials);
      
      setAuthState({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
      
      // Persist to localStorage
      localStorage.setItem('comfyrent-token', response.token);
      localStorage.setItem('comfyrent-user', JSON.stringify(response.user));
      
      if (credentials.rememberMe) {
        localStorage.setItem('comfyrent-remember', 'true');
      }
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      }));
      throw error;
    }
  };

  const register = async (data: RegisterForm): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await authService.register(data);
      
      setAuthState({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
      
      // Persist to localStorage
      localStorage.setItem('comfyrent-token', response.token);
      localStorage.setItem('comfyrent-user', JSON.stringify(response.user));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed',
      }));
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Call backend logout if available (optional since not all backends require it)
      await authService.logout();
    } catch (error) {
      // Ignore errors from backend logout - still proceed with local logout
      console.warn('Backend logout failed, proceeding with local logout:', error);
    } finally {
      // Always clear local state and storage
      setAuthState(defaultAuthState);
      
      // Clear localStorage
      localStorage.removeItem('comfyrent-token');
      localStorage.removeItem('comfyrent-user');
      localStorage.removeItem('comfyrent-remember');
    }
  };

  const forgotPassword = async (email: string): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      await authService.forgotPassword(email);
      setAuthState(prev => ({ ...prev, isLoading: false }));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to send reset email',
      }));
      throw error;
    }
  };

  const resetPassword = async (data: ResetPasswordForm): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      await authService.resetPassword(data);
      setAuthState(prev => ({ ...prev, isLoading: false }));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to reset password',
      }));
      throw error;
    }
  };

  const clearError = (): void => {
    setAuthState(prev => ({ ...prev, error: null }));
  };

  const contextValue: UseAuthReturn = {
    user: authState.user,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
    error: authState.error,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    clearError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};
