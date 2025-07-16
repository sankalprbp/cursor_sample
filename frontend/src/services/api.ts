import axios from 'axios';

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refreshToken') : null;
      if (refreshToken) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            subscribeTokenRefresh((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
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
          api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
          onRefreshed(newToken);
          return api(originalRequest);
        } catch (err) {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
        } finally {
          isRefreshing = false;
        }
      }
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
