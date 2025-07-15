import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { authService } from '../services/authService';

interface User {
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

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  demoLogin: (role: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<any>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  refreshUser: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string, confirmPassword: string) => Promise<void>;
  verifyResetToken: (token: string) => Promise<boolean>;
}

interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: string;
  company: string;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string | null } }
  | { type: 'LOGIN_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'REFRESH_TOKEN'; payload: { token: string } }
  | { type: 'SET_LOADING'; payload: boolean };

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  token: localStorage.getItem('token'),
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'REFRESH_TOKEN':
      return {
        ...state,
        token: action.payload.token,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const initializeAuth = async () => {
      console.log('AuthContext: Initializing auth...');
      const token = localStorage.getItem('token');
      console.log('AuthContext: Token from localStorage:', token ? 'exists' : 'null');
      
      if (token) {
        try {
          console.log('AuthContext: Fetching user info with token...');
          const userInfo = await authService.getUserInfo();
          console.log('AuthContext: User info received:', userInfo);
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: { user: userInfo, token },
          });
        } catch (error) {
          console.error('AuthContext: Error fetching user info with token:', error);
          localStorage.removeItem('token');
          dispatch({ type: 'LOGIN_FAILURE' });
        }
      } else {
        // Try to get user info without token (for demo mode)
        try {
          console.log('AuthContext: Fetching user info without token...');
          const userInfo = await authService.getUserInfo();
          console.log('AuthContext: User info received without token:', userInfo);
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: { user: userInfo, token: null },
          });
        } catch (error) {
          console.error('AuthContext: Error fetching user info without token:', error);
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authService.login({ email, password });
      localStorage.setItem('token', response.AccessToken);
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: response.User, token: response.AccessToken },
      });
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' });
      throw error;
    }
  };

  const demoLogin = async (role: string) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authService.demoLogin(role);
      localStorage.setItem('token', response.AccessToken);
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: response.User, token: response.AccessToken },
      });
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' });
      throw error;
    }
  };

  const register = async (userData: RegisterData) => {
    try {
      const response = await authService.register(userData);
      // Don't auto-login after registration - let user manually log in with pre-filled form
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      dispatch({ type: 'LOGOUT' });
    }
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        const response = await authService.refresh({ refresh_token: refreshToken });
        localStorage.setItem('token', response.AccessToken);
        dispatch({ type: 'REFRESH_TOKEN', payload: { token: response.AccessToken } });
      }
    } catch (error) {
      logout();
    }
  };

  const refreshUser = async () => {
    try {
      const userInfo = await authService.getUserInfo();
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: userInfo, token: state.token! },
      });
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  };

  const forgotPassword = async (email: string) => {
    await authService.forgotPassword({ email });
  };

  const resetPassword = async (token: string, newPassword: string, confirmPassword: string) => {
    await authService.resetPassword({ token, newPassword, confirmPassword });
  };

  const verifyResetToken = async (token: string): Promise<boolean> => {
    return await authService.verifyResetToken({ token });
  };

  const value: AuthContextType = {
    ...state,
    login,
    demoLogin,
    register,
    logout,
    refreshToken,
    refreshUser,
    forgotPassword,
    resetPassword,
    verifyResetToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
