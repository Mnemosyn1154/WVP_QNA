import React from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Search, FileText, TrendingUp, ArrowRight } from 'lucide-react';

const HomePage: React.FC = () => {
  const features = [
    {
      icon: <Search className="h-8 w-8 text-blue-600" />,
      title: '실시간 정보 검색',
      description: '120~250개 포트폴리오 기업의 최신 정보를 즉시 검색할 수 있습니다.',
    },
    {
      icon: <FileText className="h-8 w-8 text-blue-600" />,
      title: '재무제표 분석',
      description: 'PDF 형태의 사업보고서, 분기보고서를 AI가 분석하여 답변합니다.',
    },
    {
      icon: <TrendingUp className="h-8 w-8 text-blue-600" />,
      title: '데이터 시각화',
      description: '재무 데이터를 차트로 시각화하여 한눈에 파악할 수 있습니다.',
    },
  ];

  const exampleQuestions = [
    "삼성전자의 2024년 매출은 얼마인가요?",
    "LG전자의 최근 인수합병 소식이 있나요?",
    "SK하이닉스의 HBM 사업 현황을 알려주세요.",
    "현대자동차의 전기차 판매 실적은 어떤가요?",
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-white">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              투자 포트폴리오 Q&A 챗봇
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              AI 기반 대화형 시스템으로 포트폴리오 기업의 재무 정보와 뉴스를 
              실시간으로 조회하고 분석해보세요.
            </p>
            <Link
              to="/chat"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              <MessageSquare className="h-5 w-5 mr-2" />
              채팅 시작하기
              <ArrowRight className="h-5 w-5 ml-2" />
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            주요 기능
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Example Questions Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            이런 질문을 해보세요
          </h2>
          <div className="max-w-2xl mx-auto">
            <div className="space-y-4">
              {exampleQuestions.map((question, index) => (
                <Link
                  key={index}
                  to="/chat"
                  className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center">
                    <MessageSquare className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0" />
                    <span className="text-gray-700">{question}</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            지금 바로 시작하세요
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            투자팀의 업무 효율을 90% 향상시켜보세요.
          </p>
          <Link
            to="/chat"
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors text-lg"
          >
            채팅 시작하기
            <ArrowRight className="h-6 w-6 ml-2" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;