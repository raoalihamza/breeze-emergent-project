import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Create axios instance with interceptors
const axiosInstance = axios.create();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [impersonatedUser, setImpersonatedUser] = useState(null);
  const [originalAdmin, setOriginalAdmin] = useState(null);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setImpersonatedUser(null);
    setOriginalAdmin(null);
  }, []);

  // Set up axios interceptor to handle token expiration
  useEffect(() => {
    const interceptor = axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          const errorMessage = error.response?.data?.detail || '';
          if (errorMessage.toLowerCase().includes('token expired') || 
              errorMessage.toLowerCase().includes('invalid token')) {
            console.log('Token expired, logging out...');
            logout();
            window.location.href = '/login?expired=true';
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axiosInstance.interceptors.response.eject(interceptor);
    };
  }, [logout]);

  useEffect(() => {
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const userData = response.data;
      setUser(userData);
      
      // Check if this is an impersonation session
      if (userData.impersonated_by) {
        setImpersonatedUser(userData);
        setOriginalAdmin({
          id: userData.impersonated_by,
          name: userData.impersonated_by_name
        });
      } else {
        setImpersonatedUser(null);
        setOriginalAdmin(null);
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    const { token: newToken, user: userData } = response.data;
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    return userData;
  };

  const signup = async (email, password, name, invite_token) => {
    const response = await axios.post(`${API}/auth/signup`, {
      email,
      password,
      name,
      invite_token
    });
    const { token: newToken, user: userData } = response.data;
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    return userData;
  };

  const impersonateUser = async (userId) => {
    try {
      const response = await axios.post(`${API}/admin/impersonate/${userId}`, {}, getAuthHeader());
      const { token: newToken, user: targetUser, impersonated_by } = response.data;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(targetUser);
      setImpersonatedUser(targetUser);
      setOriginalAdmin(impersonated_by);
      
      return targetUser;
    } catch (error) {
      console.error('Failed to impersonate user:', error);
      throw error;
    }
  };

  const stopImpersonation = async () => {
    try {
      const response = await axios.post(`${API}/admin/stop-impersonation`, {}, getAuthHeader());
      const { token: newToken, user: adminUser } = response.data;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(adminUser);
      setImpersonatedUser(null);
      setOriginalAdmin(null);
      
      return adminUser;
    } catch (error) {
      console.error('Failed to stop impersonation:', error);
      throw error;
    }
  };

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${token}` }
  });

  // Use axiosInstance for API calls (has interceptor for token expiration)
  const apiCall = useCallback((config) => {
    return axiosInstance({
      ...config,
      headers: {
        ...config.headers,
        Authorization: `Bearer ${token}`
      }
    });
  }, [token]);

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      login, 
      signup, 
      logout, 
      getAuthHeader,
      apiCall,
      impersonateUser, 
      stopImpersonation,
      impersonatedUser,
      originalAdmin
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
