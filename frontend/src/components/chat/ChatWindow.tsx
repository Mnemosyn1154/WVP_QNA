import React from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ErrorAlert from '../common/ErrorAlert';
import { useChatContext } from '../../contexts/ChatContext';

const ChatWindow: React.FC = () => {
  const { messages, isLoading, error, sendMessage, clearError } = useChatContext();

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {error && (
        <div className="p-4 bg-white border-b">
          <ErrorAlert message={error} onClose={clearError} />
        </div>
      )}
      
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSendMessage={sendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatWindow;