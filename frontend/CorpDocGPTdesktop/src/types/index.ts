export interface Document {
  id: string;
  filename: string;
  uploadDate: string;
  size: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: string[];
}

export interface ChatHistoryItem {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messages: ChatMessage[];
}

export interface KnowledgeBaseStats {
  documentCount: number;
  status: string;
}

export interface RAGResponse {
  answer: string;
  sources_used: number;
  sources: string[];
  context_length: number;
}

export interface UploadResponse {
  success: boolean;
  filename: string;
  message: string;
}

export interface HealthResponse {
  status: string;
  components?: {
    knowledge_base_documents?: number;
  };
}