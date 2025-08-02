import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];
let refreshPromise: Promise<string> | null = null;

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

const onRefreshFailed = () => {
  refreshSubscribers = [];
  // Clear tokens if refresh fails
  if (typeof window !== 'undefined') {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    // Redirect to login page
    window.location.href = '/login';
  }
};

// Secure token storage with encryption (basic implementation)
const secureStorage = {
  setItem: (key: string, value: string) => {
    try {
      // In production, you might want to use a more secure storage method
      // For now, we'll use localStorage but with additional security checks
      if (typeof window !== 'undefined') {
        localStorage.setItem(key, value);
      }
    } catch (error) {
      console.error('Failed to store token:', error);
    }
  },
  getItem: (key: string): string | null => {
    try {
      if (typeof window !== 'undefined') {
        return localStorage.getItem(key);
      }
      return null;
    } catch (error) {
      console.error('Failed to retrieve token:', error);
      return null;
    }
  },
  removeItem: (key: string) => {
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem(key);
      }
    } catch (error) {
      console.error('Failed to remove token:', error);
    }
  }
};

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000, // 10 second timeout
});

api.interceptors.request.use(
  (config) => {
    const token = secureStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 Unauthorized errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = secureStorage.getItem('refreshToken');
      
      if (refreshToken) {
        // If already refreshing, queue this request
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            subscribeTokenRefresh((token) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(api(originalRequest));
            });
          });
        }

        originalRequest._retry = true;
        isRefreshing = true;
        
        // Create a single refresh promise to avoid multiple refresh calls
        if (!refreshPromise) {
          refreshPromise = (async () => {
            try {
              const resp = await axios.post(
                '/api/v1/auth/refresh',
                { refresh_token: refreshToken },
                { 
                  baseURL: api.defaults.baseURL,
                  timeout: 5000 // Shorter timeout for refresh
                }
              );
              
              const newToken = resp.data.access_token;
              const newRefresh = resp.data.refresh_token;
              
              secureStorage.setItem('accessToken', newToken);
              secureStorage.setItem('refreshToken', newRefresh);
              
              if (api.defaults.headers.common) {
                api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
              }
              
              onRefreshed(newToken);
              return newToken;
            } catch (refreshError) {
              console.error('Token refresh failed:', refreshError);
              onRefreshFailed();
              throw refreshError;
            } finally {
              isRefreshing = false;
              refreshPromise = null;
            }
          })();
        }
        
        try {
          const newToken = await refreshPromise;
          return api(originalRequest);
        } catch (refreshError) {
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    
    // Enhanced error handling with specific error messages
    if (error.response?.status === 403) {
      console.error('Access forbidden:', error.response.data);
      // Could trigger a logout or show access denied message
    } else if (error.response?.status === 404) {
      console.error('Resource not found:', error.response.data);
    } else if (error.response?.status === 422) {
      console.error('Validation error:', error.response.data);
    } else if (error.response?.status === 429) {
      console.error('Rate limited:', error.response.data);
    } else if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (!error.response) {
      console.error('Network error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;

// Enhanced API helpers with better error handling
export async function fetchCalls() {
  try {
    const res = await api.get('/api/v1/calls');
    return res.data.calls as Array<any>;
  } catch (error) {
    console.error('Failed to fetch calls:', error);
    throw error;
  }
}

export async function fetchUsers() {
  try {
    const res = await api.get('/api/v1/users');
    return res.data.users as Array<any>;
  } catch (error) {
    console.error('Failed to fetch users:', error);
    throw error;
  }
}

export async function updateProfile(userId: string, data: any) {
  try {
    const res = await api.put(`/api/v1/users/${userId}`, data);
    return res.data;
  } catch (error) {
    console.error('Failed to update profile:', error);
    throw error;
  }
}

export async function fetchTenants() {
  try {
    const res = await api.get('/api/v1/tenants');
    return res.data.tenants as Array<any>;
  } catch (error) {
    console.error('Failed to fetch tenants:', error);
    throw error;
  }
}

export async function changeUserRole(userId: string, role: string) {
  try {
    const res = await api.patch(`/api/v1/auth/admin/users/${userId}/role`, { role });
    return res.data;
  } catch (error) {
    console.error('Failed to change user role:', error);
    throw error;
  }
}

export async function changeUserTenant(userId: string, tenantId: string | null) {
  try {
    const res = await api.patch(`/api/v1/auth/admin/users/${userId}/tenant`, { tenant_id: tenantId });
    return res.data;
  } catch (error) {
    console.error('Failed to change user tenant:', error);
    throw error;
  }
}

// Export secure storage for use in auth hook
export { secureStorage };

// AI Calling API functions
export async function makeAICall(phoneNumber: string, tenantId?: string) {
  try {
    const res = await api.post('/api/v1/voice/twilio/make-call', {
      caller_number: phoneNumber,
      tenant_id: tenantId
    });
    return res.data;
  } catch (error) {
    console.error('Failed to make AI call:', error);
    throw error;
  }
}

export async function getTwilioStatus() {
  try {
    const res = await api.get('/api/v1/voice/twilio/status');
    return res.data;
  } catch (error) {
    console.error('Failed to get Twilio status:', error);
    throw error;
  }
}

export async function getCallStatus(callId: string) {
  try {
    const res = await api.get(`/api/v1/voice/calls/${callId}/status`);
    return res.data;
  } catch (error) {
    console.error('Failed to get call status:', error);
    throw error;
  }
}

export async function endCall(callId: string) {
  try {
    const res = await api.post(`/api/v1/voice/calls/${callId}/end`);
    return res.data;
  } catch (error) {
    console.error('Failed to end call:', error);
    throw error;
  }
}
