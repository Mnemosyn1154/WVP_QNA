import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8081/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    if (error.code === 'ERR_NETWORK' || error.code === 'ERR_CONNECTION_REFUSED') {
      error.message = '백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.';
    } else if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    } else if (error.response?.status === 500) {
      error.message = error.response?.data?.detail || '서버 오류가 발생했습니다.';
    }
    
    return Promise.reject(error);
  }
);

// Chat API
export const chatAPI = {
  sendMessage: async (question: string, context?: any) => {
    const response = await api.post('/chat/', { question, context });
    return response.data;
  },
  
  getChatHistory: async (limit = 50, offset = 0) => {
    const response = await api.get('/chat/history', { params: { limit, offset } });
    return response.data;
  },
};

// Document API
export const documentAPI = {
  searchDocuments: async (params: {
    company: string;
    year?: number;
    type?: string;
    limit?: number;
  }) => {
    const response = await api.get('/documents/search', { params });
    return response.data;
  },
  
  getDocument: async (id: number) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },
};

// News API
export const newsAPI = {
  searchNews: async (params: {
    company: string;
    keyword?: string;
    from?: string;
    to?: string;
    limit?: number;
  }) => {
    const response = await api.get('/news/search', { params });
    return response.data;
  },
  
  getNewsArticle: async (id: number) => {
    const response = await api.get(`/news/${id}`);
    return response.data;
  },
};

// Health API
export const healthAPI = {
  checkHealth: async () => {
    const response = await axios.get('http://127.0.0.1:8081/health');
    return response.data;
  },
  
  checkDetailedHealth: async () => {
    const response = await axios.get('http://127.0.0.1:8081/health/detailed');
    return response.data;
  },
};

export default api;