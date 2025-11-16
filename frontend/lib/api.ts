import axios from 'axios';

// Use relative URL to leverage Next.js API proxy (configured in next.config.ts)
// This works in both development and production without environment variables
const api = axios.create({
  baseURL: '/api',
});

// Add request interceptor to include authentication headers
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // Add user_id as query parameter for GET requests
    const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
    if (userId && config.method === 'get') {
      config.params = {
        ...config.params,
        user_id: userId,
      };
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Clear auth data and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('username');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;