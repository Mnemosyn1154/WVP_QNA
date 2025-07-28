import React from 'react';
import { User, Bot, Clock, FileText } from 'lucide-react';
import type { ChatMessage } from '../../types';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} max-w-3xl`}>
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center ${
              isUser ? 'bg-blue-600' : 'bg-gray-600'
            }`}
          >
            {isUser ? (
              <User className="h-6 w-6 text-white" />
            ) : (
              <Bot className="h-6 w-6 text-white" />
            )}
          </div>
        </div>

        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div
            className={`px-4 py-3 rounded-lg ${
              isUser
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>

          {/* Message metadata */}
          <div className="flex items-center mt-2 space-x-2 text-xs text-gray-500">
            <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
            
            {message.processingTime && (
              <span className="flex items-center">
                <Clock className="h-3 w-3 mr-1" />
                {message.processingTime.toFixed(1)}초
              </span>
            )}
          </div>

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600 mb-1">출처:</p>
              <div className="flex flex-wrap gap-2">
                {message.sources.map((source, index) => (
                  <div
                    key={index}
                    className="flex items-center px-2 py-1 bg-gray-200 rounded text-xs text-gray-700"
                  >
                    <FileText className="h-3 w-3 mr-1" />
                    {source}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;