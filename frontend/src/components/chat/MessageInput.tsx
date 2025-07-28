import React, { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end space-x-2">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="질문을 입력하세요... (예: 삼성전자의 최근 매출은?)"
            disabled={disabled}
            className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            rows={1}
            style={{ minHeight: '40px', maxHeight: '120px' }}
          />
          <button
            onClick={handleSubmit}
            disabled={disabled || !message.trim()}
            className="rounded-lg bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500">
          Shift + Enter로 줄바꿈을 할 수 있습니다.
        </div>
      </div>
    </div>
  );
};

export default MessageInput;