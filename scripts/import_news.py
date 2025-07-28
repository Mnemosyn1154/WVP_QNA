#!/usr/bin/env python3
"""
Import news data from JSON file into the database
"""

import asyncio
import sys
from pathlib import Path
import argparse
from datetime import datetime
import json
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.services.news_service import NewsService
from app.core.embedding_client import EmbeddingClient
from app.core.config import settings
import chromadb
from chromadb.config import Settings as ChromaSettings


def get_chromadb_client() -> chromadb.Client:
    """Get ChromaDB client"""
    try:
        return chromadb.HttpClient(
            host="localhost",
            port=8000,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    except Exception as e:
        logger.warning(f"Could not connect to ChromaDB server: {e}")
        return chromadb.PersistentClient(path="./chromadb_data")


def create_sample_news_data(output_file: str):
    """Create sample news data for testing"""
    
    sample_news = [
        {
            "company_name": "삼성전자",
            "title": "삼성전자, 2024년 4분기 영업이익 6.5조원 기록",
            "content": "삼성전자가 2024년 4분기 영업이익 6.5조원을 기록하며 시장 예상치를 상회했다. 메모리 반도체 가격 상승과 스마트폰 판매 호조가 실적 개선의 주요 원인으로 분석된다.",
            "content_url": "https://news.example.com/samsung-q4-2024",
            "source": "한국경제신문",
            "published_date": "2025-01-25T09:00:00"
        },
        {
            "company_name": "삼성전자",
            "title": "삼성전자, AI 반도체 시장 진출 본격화",
            "content": "삼성전자가 차세대 AI 반도체 개발에 10조원을 투자한다고 발표했다. 2025년 하반기 양산을 목표로 하고 있으며, 글로벌 AI 칩 시장에서의 경쟁력 확보를 노린다.",
            "content_url": "https://news.example.com/samsung-ai-chip",
            "source": "매일경제",
            "published_date": "2025-01-20T14:30:00"
        },
        {
            "company_name": "LG전자",
            "title": "LG전자, 전장사업부 매출 사상 최대치 달성",
            "content": "LG전자의 전장사업부가 2024년 연간 매출 10조원을 돌파하며 사상 최대 실적을 기록했다. 전기차 시장 성장과 함께 배터리, 인포테인먼트 시스템 수주가 크게 늘었다.",
            "content_url": "https://news.example.com/lg-auto-record",
            "source": "서울경제",
            "published_date": "2025-01-22T11:00:00"
        },
        {
            "company_name": "SK하이닉스",
            "title": "SK하이닉스, HBM3E 양산 시작... AI 시장 공략",
            "content": "SK하이닉스가 차세대 고대역폭 메모리 HBM3E의 양산을 시작했다. 엔비디아 등 주요 AI 칩 제조사에 공급될 예정이며, AI 서버 시장에서의 점유율 확대가 기대된다.",
            "content_url": "https://news.example.com/sk-hbm3e",
            "source": "전자신문",
            "published_date": "2025-01-23T13:45:00"
        },
        {
            "company_name": "현대자동차",
            "title": "현대차, 인도 시장에서 연간 판매 100만대 돌파",
            "content": "현대자동차가 인도 시장에서 연간 판매량 100만대를 처음으로 돌파했다. 인도 내 전기차 생산 시설 확충과 현지화 전략이 주효했다는 평가다.",
            "content_url": "https://news.example.com/hyundai-india",
            "source": "한국일보",
            "published_date": "2025-01-21T10:30:00"
        },
        {
            "company_name": "네이버",
            "title": "네이버, 자체 개발 LLM '하이퍼클로바X' 글로벌 출시",
            "content": "네이버가 자체 개발한 대규모 언어모델 '하이퍼클로바X'를 글로벌 시장에 출시한다. 한국어와 영어, 일본어를 지원하며, 기업용 AI 서비스 시장을 공략할 계획이다.",
            "content_url": "https://news.example.com/naver-hyperclova",
            "source": "디지털타임스",
            "published_date": "2025-01-24T15:00:00"
        },
        {
            "company_name": "카카오",
            "title": "카카오뱅크, 2024년 당기순이익 5000억원 돌파",
            "content": "카카오뱅크가 2024년 당기순이익 5000억원을 돌파하며 흑자 기조를 이어갔다. 대출 자산의 질적 개선과 수수료 수익 증가가 실적 향상의 주요 요인으로 꼽힌다.",
            "content_url": "https://news.example.com/kakaobank-profit",
            "source": "이데일리",
            "published_date": "2025-01-19T09:30:00"
        },
        {
            "company_name": "셀트리온",
            "title": "셀트리온, 바이오시밀러 신약 FDA 승인 획득",
            "content": "셀트리온이 개발한 자가면역질환 치료제 바이오시밀러가 미국 FDA 승인을 받았다. 연간 1조원 규모의 시장 진출이 가능해져 매출 성장이 기대된다.",
            "content_url": "https://news.example.com/celltrion-fda",
            "source": "머니투데이",
            "published_date": "2025-01-18T16:20:00"
        }
    ]
    
    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_news, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Created sample news data file: {output_path}")
    logger.info(f"Total news items: {len(sample_news)}")
    
    return len(sample_news)


async def import_news_from_file(file_path: str):
    """Import news from JSON file"""
    
    # Initialize services
    chromadb_client = get_chromadb_client()
    embedding_client = EmbeddingClient()
    news_service = NewsService(chromadb_client, embedding_client)
    
    # Check if file exists
    if not Path(file_path).exists():
        raise FileNotFoundError(f"News file not found: {file_path}")
    
    async with AsyncSessionLocal() as db:
        try:
            result = await news_service.index_news_from_file(file_path, db)
            return result
        except Exception as e:
            logger.error(f"Error importing news: {str(e)}")
            raise


async def verify_imported_news():
    """Verify imported news in the database"""
    from app.models.news import News
    from sqlalchemy import select, func
    
    async with AsyncSessionLocal() as db:
        # Count total news
        count_result = await db.execute(select(func.count(News.id)))
        total_news = count_result.scalar()
        
        # Get news statistics by company
        stats_result = await db.execute(
            select(
                News.company_name,
                func.count(News.id).label('count'),
                func.min(News.published_date).label('oldest'),
                func.max(News.published_date).label('newest')
            ).group_by(News.company_name)
        )
        
        stats = stats_result.all()
        
        # Get recent news
        recent_result = await db.execute(
            select(News)
            .order_by(News.published_date.desc())
            .limit(5)
        )
        recent_news = recent_result.scalars().all()
        
        return {
            "total_news": total_news,
            "by_company": [
                {
                    "company": stat.company_name,
                    "count": stat.count,
                    "date_range": f"{stat.oldest.date() if stat.oldest else 'N/A'} ~ {stat.newest.date() if stat.newest else 'N/A'}"
                }
                for stat in stats
            ],
            "recent_news": [
                {
                    "title": news.title,
                    "company": news.company_name,
                    "date": news.published_date.strftime("%Y-%m-%d") if news.published_date else "N/A"
                }
                for news in recent_news
            ]
        }


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Import news data")
    parser.add_argument(
        "--file",
        help="JSON file containing news data"
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create sample news data file"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify imported news"
    )
    
    args = parser.parse_args()
    
    logger.info("Starting news import script...")
    
    if args.create_sample:
        # Create sample data
        sample_file = "data/sample_news.json"
        count = create_sample_news_data(sample_file)
        print(f"\n✅ Created sample news file: {sample_file}")
        print(f"   Contains {count} news items")
        print(f"\nTo import this data, run:")
        print(f"   python {sys.argv[0]} --file {sample_file}")
    
    elif args.verify:
        # Verify imported news
        logger.info("Verifying imported news...")
        stats = await verify_imported_news()
        
        print("\n=== News Database Statistics ===")
        print(f"Total news articles: {stats['total_news']}")
        
        print("\nBy Company:")
        for company_stat in stats['by_company']:
            print(f"  - {company_stat['company']}: {company_stat['count']} articles")
            print(f"    Date range: {company_stat['date_range']}")
        
        if stats['recent_news']:
            print("\nRecent Articles:")
            for i, news in enumerate(stats['recent_news'], 1):
                print(f"  {i}. [{news['date']}] {news['company']}: {news['title'][:60]}...")
    
    elif args.file:
        # Import news from file
        result = await import_news_from_file(args.file)
        
        print("\n=== Import Results ===")
        print(f"Total items in file: {result['total_items']}")
        print(f"Successfully imported: {result['indexed']}")
        print(f"Errors: {result['errors']}")
        
        if result['error_details']:
            print("\nError details:")
            for error in result['error_details'][:5]:
                print(f"  - {error}")
    
    else:
        parser.print_help()
        print("\nExamples:")
        print(f"  python {sys.argv[0]} --create-sample")
        print(f"  python {sys.argv[0]} --file data/sample_news.json")
        print(f"  python {sys.argv[0]} --verify")
    
    logger.info("Script completed!")


if __name__ == "__main__":
    asyncio.run(main())