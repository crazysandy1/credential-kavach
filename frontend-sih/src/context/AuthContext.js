import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is logged in on app start
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await apiService.getCurrentUser();
          console.log('Auth initialization user data:', userData); // Debug log
          
          // Ensure admin account is always approved
          if (userData.email === 'admin@credentialkavach.gov.in') {
            userData.is_approved = true;
            userData.is_verified = true;
            userData.is_active = true;
            console.log('Admin account approval ensured during auth init'); // Debug log
          }
          
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Auth initialization failed:', error); // Debug log
          localStorage.removeItem('token');
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const { user: userData, token } = await apiService.login(credentials);
      console.log('Login response user data:', userData); // Debug log
      
      // Ensure admin account is always approved
      if (userData.email === 'admin@credentialkavach.gov.in') {
        userData.is_approved = true;
        userData.is_verified = true;
        userData.is_active = true;
        console.log('Admin account approved status ensured'); // Debug log
      }
      
      localStorage.setItem('token', token);
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (error) {
      console.error('Login error:', error); // Debug log
      throw error;
    }
  };

  const signup = async (userData) => {
    try {
      const response = await apiService.signup(userData);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateUser = (userData) => {
    setUser(userData);
  };

  const hasRole = (requiredRole) => {
    return user && user.role === requiredRole;
  };

  const getDashboardRoute = () => {
    if (!user) return '/login';
    
    switch (user.role) {
      case 'student':
        return '/student-dashboard';
      case 'college':
        return '/college-dashboard';
      case 'government':
        return '/government-dashboard';
      case 'employer':
        return '/employer-dashboard';
      default:
        return '/';
    }
  };

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    signup,
    logout,
    updateUser,
    hasRole,
    getDashboardRoute,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};