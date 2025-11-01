import axios from 'axios';
import { Document, KnowledgeBaseStats, RAGResponse, UploadResponse, HealthResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, 
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

  // Это старый метод chat. В нем нет потокового ответа.
  chat: async (message: string): Promise<RAGResponse> => {
    const response = await api.post('/api/rag/query', { question: message });
    return response.data;
  },

  chatStream: async (question: string, onChunk: (chunk: any) => void): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error('Streaming request failed');
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onChunk(data);
            } catch (e) {
              console.error('Error parsing chunk:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
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