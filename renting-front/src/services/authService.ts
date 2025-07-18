import { apiService } from './apiService';
import { LoginForm, RegisterForm, ResetPasswordForm, User, ApiResponse, API_ENDPOINTS } from '@/types';

export const authService = {
  async login(credentials: LoginForm): Promise<{ user: User; token: string }> {
    // Your backend expects JSON format with email and password
    const loginData = {
      email: credentials.email,
      password: credentials.password
    };
    
    const response = await apiService.post<{ access_token: string; token_type: string; user: User }>(
      API_ENDPOINTS.LOGIN, 
      loginData,
      { requiresAuth: false }
    );
    
    return {
      user: response.user,
      token: response.access_token
    };
  },

  async register(data: RegisterForm): Promise<{ user: User; token: string }> {
    // Transform frontend data to match backend schema
    const registerData = {
      email: data.email,
      password: data.password,
      first_name: data.firstName,
      last_name: data.lastName,
      phone: data.phone,
      role: data.role || 'tenant'
    };
    
    const response = await apiService.post<{ user: User; access_token: string }>(
      API_ENDPOINTS.REGISTER, 
      registerData,
      { requiresAuth: false }
    );
    return {
      user: response.user,
      token: response.access_token
    };
  },

  async logout(): Promise<void> {
    await apiService.post<void>(API_ENDPOINTS.LOGOUT);
  },

  async forgotPassword(email: string): Promise<void> {
    await apiService.post<void>(
      API_ENDPOINTS.FORGOT_PASSWORD, 
      { email },
      { requiresAuth: false }
    );
  },

  async resetPassword(data: ResetPasswordForm): Promise<void> {
    await apiService.post<void>(
      API_ENDPOINTS.RESET_PASSWORD, 
      data,
      { requiresAuth: false }
    );
  },

  async refreshToken(): Promise<{ user: User; token: string }> {
    // For FastAPI, we'll just validate the current token and get user info
    const response = await apiService.get<User>(
      API_ENDPOINTS.PROFILE
    );
    
    // Return current token since FastAPI handles token validation
    const currentToken = localStorage.getItem('comfyrent-token') || '';
    
    return {
      user: response,
      token: currentToken
    };
  },

  async verifyEmail(token: string): Promise<void> {
    await apiService.post<void>(
      API_ENDPOINTS.VERIFY_EMAIL, 
      { token },
      { requiresAuth: false }
    );
  },
};
