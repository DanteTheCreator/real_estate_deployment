import { API_ENDPOINTS } from '@/types';

// Resolve API base URL robustly for prod/staging/dev
function resolveBaseUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL as string | undefined;
  if (envUrl && envUrl.trim().length > 0) {
    const u = envUrl.trim();
    // Absolute URL provided
    if (u.startsWith('http://') || u.startsWith('https://')) {
      return u.replace(/\/$/, '');
    }
    // Relative path (e.g. /api) -> prefer same-origin proxy; on :3000 map to backend :8000
    if (u.startsWith('/')) {
      const origin = window.location.origin;
      if (origin.includes(':3000')) {
        return origin.replace(':3000', ':8000') + u;
      }
      return `${origin}${u}`.replace(/\/$/, '');
    }
  }
  // No env set: prefer same-origin /api if behind reverse proxy
  const origin = window.location.origin;
  if (origin.includes(':3000')) {
    // Common docker compose mapping: send to backend on :8000
    return origin.replace(':3000', ':8000') + '/api';
  }
  return origin + '/api';
}

// Base API configuration
const API_BASE_URL = resolveBaseUrl();

interface RequestConfig extends RequestInit {
  requiresAuth?: boolean;
}

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private getAuthToken(): string | null {
    return localStorage.getItem('comfyrent-token');
  }

  private getDefaultHeaders(): HeadersInit {
    const headers: HeadersInit = {};

    const token = this.getAuthToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = Array.isArray(errorData.detail) 
            ? errorData.detail.map((e: { msg?: string; message?: string }) => e.msg || e.message).join(', ')
            : errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (e) {
        // If we can't parse the error response, use the default message
      }
      
      throw new Error(errorMessage);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }

    return response.text() as unknown as T;
  }

  async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const { requiresAuth = true, ...requestConfig } = config;
    
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      ...this.getDefaultHeaders(),
      ...requestConfig.headers,
    } as Record<string, string>;

    // Set Content-Type for JSON if not already set and body is not FormData
    if (requestConfig.body && !(requestConfig.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    // Check if auth is required but token is missing
    if (requiresAuth && !this.getAuthToken()) {
      throw new Error('Authentication required');
    }

    const response = await fetch(url, {
      ...requestConfig,
      headers,
      credentials: 'include',
    });

    return this.handleResponse<T>(response);
  }

  // HTTP Methods
  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data instanceof FormData ? data : (data ? JSON.stringify(data) : undefined),
    });
  }

  async put<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }

  // File upload method
  async uploadFile<T>(endpoint: string, file: File, config?: RequestConfig): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const headers = { ...this.getDefaultHeaders() } as Record<string, string>;
    delete headers['Content-Type']; // Let browser set multipart boundary

    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: formData as unknown as BodyInit,
      headers,
    });
  }

  // Multiple file upload
  async uploadFiles<T>(endpoint: string, files: File[], config?: RequestConfig): Promise<T> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const headers = { ...this.getDefaultHeaders() } as Record<string, string>;
    delete headers['Content-Type']; // Let browser set multipart boundary

    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: formData as unknown as BodyInit,
      headers,
    });
  }

  // Query string builder for GET requests
  buildQueryString(params: Record<string, unknown>): string {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(item => searchParams.append(key, item.toString()));
        } else {
          searchParams.append(key, value.toString());
        }
      }
    });

    const queryString = searchParams.toString();
    return queryString ? `?${queryString}` : '';
  }
}

// Create and export singleton instance
export const apiService = new ApiService();
