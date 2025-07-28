import React, { useState } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  RefreshCw,
  Database,
  Server,
  HardDrive,
  Activity
} from 'lucide-react';
import { healthAPI, chatAPI, documentAPI, newsAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

interface TestResult {
  name: string;
  status: 'pending' | 'testing' | 'success' | 'error';
  message?: string;
  data?: any;
}

const TestPage: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const testCases = [
    {
      name: '기본 헬스체크',
      test: async () => {
        const result = await healthAPI.checkHealth();
        return { success: true, data: result };
      },
    },
    {
      name: '상세 헬스체크',
      test: async () => {
        const result = await healthAPI.checkDetailedHealth();
        return { success: true, data: result };
      },
    },
    {
      name: '채팅 API 테스트',
      test: async () => {
        const result = await chatAPI.sendMessage('테스트 메시지입니다.');
        return { success: true, data: result };
      },
    },
    {
      name: '문서 검색 테스트',
      test: async () => {
        const result = await documentAPI.searchDocuments({ 
          company: '삼성전자',
          limit: 5 
        });
        return { success: true, data: result };
      },
    },
    {
      name: '뉴스 검색 테스트',
      test: async () => {
        const result = await newsAPI.searchNews({ 
          company: '삼성전자',
          limit: 5 
        });
        return { success: true, data: result };
      },
    },
  ];

  const runTests = async () => {
    setIsRunning(true);
    const results: TestResult[] = testCases.map(tc => ({
      name: tc.name,
      status: 'pending' as const,
    }));
    setTestResults(results);

    for (let i = 0; i < testCases.length; i++) {
      // Update to testing
      results[i].status = 'testing';
      setTestResults([...results]);

      try {
        const testResult = await testCases[i].test();
        results[i].status = 'success';
        results[i].data = testResult.data;
        results[i].message = '성공';
      } catch (error) {
        results[i].status = 'error';
        results[i].message = error instanceof Error ? error.message : '알 수 없는 오류';
      }

      setTestResults([...results]);
    }

    setIsRunning(false);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
      case 'testing':
        return <LoadingSpinner size="sm" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
    }
  };

  const getServiceIcon = (serviceName: string) => {
    if (serviceName.includes('PostgreSQL')) return <Database className="h-4 w-4" />;
    if (serviceName.includes('Redis')) return <Server className="h-4 w-4" />;
    if (serviceName.includes('ChromaDB')) return <HardDrive className="h-4 w-4" />;
    return <Activity className="h-4 w-4" />;
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          API 테스트 대시보드
        </h1>
        <p className="text-gray-600 mb-6">
          백엔드 API와 데이터베이스 연결 상태를 확인합니다.
        </p>
        
        <button
          onClick={runTests}
          disabled={isRunning}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw className={`h-5 w-5 mr-2 ${isRunning ? 'animate-spin' : ''}`} />
          {isRunning ? '테스트 진행 중...' : '테스트 실행'}
        </button>
      </div>

      {testResults.length > 0 && (
        <div className="space-y-4">
          {testResults.map((result, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md p-6 transition-all"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(result.status)}
                  <h3 className="text-lg font-semibold text-gray-900">
                    {result.name}
                  </h3>
                </div>
                {result.message && (
                  <span
                    className={`text-sm ${
                      result.status === 'error' ? 'text-red-600' : 'text-green-600'
                    }`}
                  >
                    {result.message}
                  </span>
                )}
              </div>

              {result.data && (
                <div className="mt-4">
                  {/* Special handling for detailed health check */}
                  {result.name === '상세 헬스체크' && result.data.dependencies && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        서비스 상태:
                      </p>
                      {Object.entries(result.data.dependencies).map(([service, info]: [string, any]) => (
                        <div
                          key={service}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded"
                        >
                          <div className="flex items-center space-x-2">
                            {getServiceIcon(service)}
                            <span className="text-sm font-medium capitalize">
                              {service}
                            </span>
                          </div>
                          <span
                            className={`text-sm ${
                              info.status === 'healthy'
                                ? 'text-green-600'
                                : 'text-red-600'
                            }`}
                          >
                            {info.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Default data display */}
                  {result.name !== '상세 헬스체크' && (
                    <div className="bg-gray-50 rounded p-4 overflow-auto max-h-60">
                      <pre className="text-xs text-gray-700">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Quick Test Samples */}
      <div className="mt-12 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          빠른 테스트 예제
        </h2>
        <div className="space-y-3">
          <div className="p-3 bg-gray-50 rounded">
            <p className="text-sm font-medium text-gray-700">채팅 테스트:</p>
            <code className="text-xs text-gray-600">
              "삼성전자의 최근 매출은 얼마인가요?"
            </code>
          </div>
          <div className="p-3 bg-gray-50 rounded">
            <p className="text-sm font-medium text-gray-700">문서 검색:</p>
            <code className="text-xs text-gray-600">
              company: "LG전자", year: 2024
            </code>
          </div>
          <div className="p-3 bg-gray-50 rounded">
            <p className="text-sm font-medium text-gray-700">뉴스 검색:</p>
            <code className="text-xs text-gray-600">
              company: "SK하이닉스", keyword: "HBM"
            </code>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestPage;