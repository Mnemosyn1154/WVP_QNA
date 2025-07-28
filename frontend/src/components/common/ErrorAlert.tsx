import React from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
  onClose?: () => void;
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onClose }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
      <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
      <div className="flex-1">
        <p className="text-sm text-red-800">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-3 text-red-600 hover:text-red-800 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  );
};

export default ErrorAlert;