import axios from 'axios';
import type { Call, VoiceProfile, Conversation, DashboardStats, CallListResponse } from '@/types';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const callsApi = {
  list: (page = 1, pageSize = 20) =>
    api.get<CallListResponse>('/calls', { params: { page, page_size: pageSize } }),

  get: (id: string) =>
    api.get<Call>(`/calls/${id}`),

  makeCall: (toNumber: string, message?: string) =>
    api.post('/calls/outbound', { to_number: toNumber, message }),

  getConversation: (callId: string) =>
    api.get<Conversation>(`/calls/${callId}/conversation`),
};

export const voicesApi = {
  list: () =>
    api.get<VoiceProfile[]>('/voices'),

  get: (id: string) =>
    api.get<VoiceProfile>(`/voices/${id}`),

  create: (data: FormData) =>
    api.post<VoiceProfile>('/voices/clone', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  test: (id: string, text: string) =>
    api.post(`/voices/${id}/test`, { text }),

  delete: (id: string) =>
    api.delete(`/voices/${id}`),
};

export const dashboardApi = {
  getStats: () =>
    api.get<DashboardStats>('/dashboard/stats'),

  getRecentCalls: (limit = 10) =>
    api.get<Call[]>('/dashboard/recent', { params: { limit } }),
};

export const healthApi = {
  check: () =>
    api.get('/health'),
};

export default api;
