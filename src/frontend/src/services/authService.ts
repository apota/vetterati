import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data.data;
          localStorage.setItem('token', access_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  user: User;
}

export interface ApiResponse<T> {
  data: T;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RegisterRequest {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: string;
  company: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  firstName?: string;
  lastName?: string;
  company?: string;
  roles: string[];
  isActive: boolean;
  lastLoginAt?: string;
  createdAt: string;
  updatedAt: string;
  preferences?: {
    timezone?: string;
    emailNotifications?: boolean;
    pushNotifications?: boolean;
    marketingEmails?: boolean;
  };
}

export interface UpdateProfileRequest {
  firstName?: string;
  lastName?: string;
  company?: string;
  preferences?: {
    timezone?: string;
    emailNotifications?: boolean;
    pushNotifications?: boolean;
    marketingEmails?: boolean;
  };
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

export interface VerifyResetTokenRequest {
  token: string;
}

export interface DemoLoginRequest {
  role: string;
}

export interface DemoUserInfo {
  role: string;
  name: string;
  email: string;
  description: string;
}

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response: AxiosResponse<ApiResponse<LoginResponse>> = await api.post('/api/v1/auth/email-login', credentials);
    const loginData = response.data.data;
    if (loginData.refreshToken) {
      localStorage.setItem('refresh_token', loginData.refreshToken);
    }
    return loginData;
  },

  register: async (userData: RegisterRequest): Promise<LoginResponse> => {
    const response: AxiosResponse<ApiResponse<LoginResponse>> = await api.post('/api/v1/auth/register', userData);
    const loginData = response.data.data;
    if (loginData.refreshToken) {
      localStorage.setItem('refresh_token', loginData.refreshToken);
    }
    return loginData;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/v1/auth/logout');
  },

  refresh: async (request: RefreshRequest): Promise<LoginResponse> => {
    const response: AxiosResponse<ApiResponse<LoginResponse>> = await api.post('/api/v1/auth/refresh', request);
    return response.data.data;
  },

  getUserInfo: async (): Promise<User> => {
    const response: AxiosResponse<{ data: User }> = await api.get('/api/v1/auth/me');
    return response.data.data;
  },

  forgotPassword: async (request: ForgotPasswordRequest): Promise<any> => {
    const response = await api.post('/api/v1/auth/forgot-password', request);
    return response.data.data;
  },

  verifyResetToken: async (request: VerifyResetTokenRequest): Promise<boolean> => {
    try {
      await api.post('/api/v1/auth/verify-reset-token', request);
      return true;
    } catch (error) {
      return false;
    }
  },

  resetPassword: async (request: ResetPasswordRequest): Promise<void> => {
    await api.post('/api/v1/auth/reset-password', request);
  },

  updateProfile: async (request: UpdateProfileRequest): Promise<User> => {
    const response: AxiosResponse<ApiResponse<User>> = await api.put('/api/v1/auth/me', request);
    return response.data.data;
  },

  demoLogin: async (role: string): Promise<LoginResponse> => {
    const response: AxiosResponse<ApiResponse<LoginResponse>> = await api.post('/api/v1/auth/demo-login', { role });
    const loginData = response.data.data;
    if (loginData.refreshToken) {
      localStorage.setItem('refresh_token', loginData.refreshToken);
    }
    return loginData;
  },

  getDemoUsers: async (): Promise<DemoUserInfo[]> => {
    const response: AxiosResponse<ApiResponse<DemoUserInfo[]>> = await api.get('/api/v1/auth/demo-users');
    return response.data.data;
  },
};

export default api;
