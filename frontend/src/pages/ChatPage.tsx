import React from 'react';
import ChatWindow from '../components/chat/ChatWindow';

const ChatPage: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      <div className="bg-white border-b px-4 py-3">
        <h1 className="text-xl font-semibold text-gray-800">
          포트폴리오 Q&A 채팅
        </h1>
        <p className="text-sm text-gray-600">
          투자 포트폴리오 기업에 대한 질문을 입력하세요.
        </p>
      </div>
      <div className="flex-1 overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  );
};

export default ChatPage;