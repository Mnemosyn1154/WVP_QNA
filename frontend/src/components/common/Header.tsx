import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, Home, FlaskConical } from 'lucide-react';

const Header: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <MessageSquare className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-800">Portfolio Q&A</span>
          </Link>

          <nav className="flex space-x-6">
            <Link
              to="/"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Home className="h-4 w-4" />
              <span>홈</span>
            </Link>
            
            <Link
              to="/chat"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/chat') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <MessageSquare className="h-4 w-4" />
              <span>채팅</span>
            </Link>
            
            <Link
              to="/test"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/test') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <FlaskConical className="h-4 w-4" />
              <span>테스트</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;