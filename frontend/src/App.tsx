import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChatProvider } from './contexts/ChatContext';
import Header from './components/common/Header';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import TestPage from './pages/TestPage';

function App() {
  return (
    <Router>
      <ChatProvider>
        <div className="flex flex-col h-screen">
          <Header />
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/test" element={<TestPage />} />
            </Routes>
          </main>
        </div>
      </ChatProvider>
    </Router>
  );
}

export default App;