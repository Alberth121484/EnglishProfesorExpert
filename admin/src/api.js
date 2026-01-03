import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const adminApi = {
  getOverview: () => api.get('/admin/overview'),
  getUsers: (params) => api.get('/admin/users', { params }),
  getChurnedUsers: (daysInactive = 14) => api.get('/admin/users/churned', { params: { days_inactive: daysInactive } }),
  getUserDetail: (userId) => api.get(`/admin/user/${userId}`),
  getUsageByLevel: () => api.get('/admin/usage-by-level'),
  getDailyStats: (days = 30) => api.get('/admin/daily-stats', { params: { days } }),
  getTokenUsage: (limit = 50) => api.get('/admin/token-usage', { params: { limit } }),
  getEngagement: () => api.get('/admin/engagement'),
};

export default api;
