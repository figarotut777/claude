import axios from 'axios';

// Change this to your backend URL
const API_BASE_URL = __DEV__
  ? 'http://localhost:3000/api'  // Development
  : 'https://your-production-api.com/api';  // Production

export const WEBSOCKET_URL = __DEV__
  ? 'http://localhost:3000'
  : 'https://your-production-api.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens here
    // const token = getAuthToken();
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
      throw error.response.data;
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.request);
      throw { error: { message: 'Network error. Please check your connection.' } };
    } else {
      console.error('Error:', error.message);
      throw { error: { message: error.message } };
    }
  }
);

export default api;
