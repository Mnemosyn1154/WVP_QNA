// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
  charts?: ChartData[];
  processingTime?: number;
}

export interface ChatRequest {
  question: string;
  context?: any;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  charts?: ChartData[];
  processingTime?: number;
}

// Chart types
export interface ChartData {
  type: 'line' | 'bar' | 'pie';
  title: string;
  data: any;
  options?: any;
}

// Document types
export interface Document {
  id: number;
  companyName: string;
  docType?: string;
  year: number;
  quarter?: number;
  filePath: string;
  fileSize?: number;
  createdAt: string;
  updatedAt: string;
}

// News types
export interface NewsArticle {
  id: number;
  companyName: string;
  title: string;
  content?: string;
  contentUrl?: string;
  source?: string;
  publishedDate?: string;
  createdAt: string;
  updatedAt: string;
}

// Health check types
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: string;
  version: string;
  dependencies?: {
    [key: string]: {
      status: 'healthy' | 'unhealthy';
      error?: string;
      statusCode?: number;
    };
  };
}