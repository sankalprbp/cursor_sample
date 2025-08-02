import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

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

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
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
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refreshToken') : null;
      
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
        
        try {
          const resp = await axios.post(
            '/api/v1/auth/refresh',
            { refresh_token: refreshToken },
            { baseURL: api.defaults.baseURL }
          );
          
          const newToken = resp.data.access_token;
          const newRefresh = resp.data.refresh_token;
          
          localStorage.setItem('accessToken', newToken);
          localStorage.setItem('refreshToken', newRefresh);
          
          if (api.defaults.headers.common) {
            api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
          }
          
          onRefreshed(newToken);
          return api(originalRequest);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          onRefreshFailed();
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      } else {
        // No refresh token available
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    
    // Handle other error types
    if (error.response?.status === 403) {
      console.error('Access forbidden:', error.response.data);
    } else if (error.response?.status === 404) {
      console.error('Resource not found:', error.response.data);
    } else if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

export default api;

// Convenience API helpers
export async function fetchCalls() {
  const res = await api.get('/api/v1/calls');
  return res.data.calls as Array<any>;
}

export async function fetchUsers() {
  const res = await api.get('/api/v1/users');
  return res.data.users as Array<any>;
}

export async function updateProfile(userId: string, data: any) {
  const res = await api.put(`/api/v1/users/${userId}`, data);
  return res.data;
}

export async function fetchTenants() {
  const res = await api.get('/api/v1/tenants');
  return res.data.tenants as Array<any>;
}

export async function changeUserRole(userId: string, role: string) {
  const res = await api.patch(`/api/v1/auth/admin/users/${userId}/role`, { role });
  return res.data;
}

export async function changeUserTenant(userId: string, tenantId: string | null) {
  const res = await api.patch(`/api/v1/auth/admin/users/${userId}/tenant`, { tenant_id: tenantId });
  return res.data;
}
