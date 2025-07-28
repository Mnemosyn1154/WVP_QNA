import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import LoadingSpinner from '../common/LoadingSpinner';
import type { ChatMessage } from '../../types';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 text-lg mb-2">채팅을 시작해보세요!</p>
          <p className="text-gray-400 text-sm">
            투자 포트폴리오 기업에 대한 질문을 입력하면 AI가 답변해드립니다.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="max-w-4xl mx-auto">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex flex-row max-w-3xl">
              <div className="flex-shrink-0 mr-3">
                <div className="w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center">
                  <LoadingSpinner size="sm" className="text-white" />
                </div>
              </div>
              <div className="px-4 py-3 rounded-lg bg-gray-100">
                <div className="flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span className="text-gray-600">응답을 생성하고 있습니다...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;