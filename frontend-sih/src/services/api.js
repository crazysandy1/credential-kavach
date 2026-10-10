import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:5001',
  timeout: 30000, // 30 seconds
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

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service methods
export const apiService = {
  // Authentication
  async login(credentials) {
    try {
      const response = await api.post('/api/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async signup(userData) {
    try {
      const response = await api.post('/api/auth/signup', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async getCurrentUser() {
    try {
      const response = await api.get('/api/auth/profile');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Documents
  async getDocuments() {
    try {
      const response = await api.get('/api/documents');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async uploadDocument(formData) {
    try {
      const response = await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async getDocument(documentId) {
    try {
      const response = await api.get(`/api/documents/${documentId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async verifyDocument(documentId, verificationData) {
    try {
      const response = await api.post(`/api/documents/${documentId}/verify`, verificationData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async downloadDocument(documentId) {
    try {
      const response = await api.get(`/api/documents/${documentId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Admin endpoints (Government role only)
  async getAllUsers(filters = {}) {
    try {
      const params = new URLSearchParams(filters).toString();
      const response = await api.get(`/api/admin/users?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async approveUser(userId, approvalData) {
    try {
      const response = await api.post(`/api/admin/users/${userId}/approve`, approvalData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async getAuditLogs(page = 1, limit = 50) {
    try {
      const response = await api.get(`/api/admin/audit-logs?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async getSystemStats() {
    try {
      const response = await api.get('/api/admin/stats/system');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // College-specific endpoints
  async getCollegeDocuments(filters = {}) {
    try {
      const params = new URLSearchParams(filters).toString();
      const response = await api.get(`/api/college/documents?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async getCollegeStats() {
    try {
      const response = await api.get('/api/college/stats');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Utility methods
  handleError(error) {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const { data, status } = error.response;
      return {
        message: data?.message || `Server error (${status})`,
        status,
        details: data?.details || null,
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'Unable to connect to server. Please check your internet connection.',
        status: 0,
        details: null,
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'An unexpected error occurred',
        status: -1,
        details: null,
      };
    }
  },

  // File download helper
  async downloadFile(documentId, filename) {
    try {
      const blob = await this.downloadDocument(documentId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || 'document';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Employer specific
  async updateEmployerProfile(profileData) {
    try {
      const response = await api.put('/api/employer/profile', profileData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async verifyStudentDocument(verificationData) {
    try {
      const response = await api.post('/api/verify-document', verificationData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async submitVerification(verificationData) {
    try {
      const response = await api.post('/api/employer/verify-document', verificationData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },
};

export default api;