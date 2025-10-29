import axios from 'axios';
import { Document, KnowledgeBaseStats, RAGResponse, UploadResponse, HealthResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    if (error.code === 'ECONNREFUSED') {
      throw new Error('Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд на localhost:8000');
    }
    throw error;
  }
);

export const apiService = {
  uploadDocument: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/rag/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getDocuments: async (): Promise<Document[]> => {
    try {
      const response = await api.get('/api/rag/documents');
      return response.data;
    } catch (error) {
      console.error('Error fetching documents:', error);
      return [];
    }
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    await api.delete(`/api/rag/documents/${documentId}`);
  },

  // Этот метод теперь используется для чата
  queryDocuments: async (question: string): Promise<RAGResponse> => {
    const response = await api.post('/api/rag/query', { question });
    return response.data;
  },

  // Старый метод chat можно удалить или оставить для совместимости
  chat: async (message: string): Promise<RAGResponse> => {
    const response = await api.post('/api/rag/query', { question: message });
    return response.data;
  },

  getStats: async (): Promise<KnowledgeBaseStats> => {
    const response = await api.get('/api/rag/stats');
    return response.data;
  },

  getHealth: async (): Promise<HealthResponse> => {
    const response = await api.get('/health');
    return response.data;
  },
};