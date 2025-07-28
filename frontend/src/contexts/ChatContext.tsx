import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type { ChatMessage, ChatResponse } from '../types';
import { chatAPI } from '../services/api';

interface ChatContextType {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  clearError: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    // Clear any previous errors
    setError(null);
    
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to API
      const response: ChatResponse = await chatAPI.sendMessage(content);
      
      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        charts: response.charts,
        processingTime: response.processingTime,
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : '메시지 전송 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value = {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    clearError,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};