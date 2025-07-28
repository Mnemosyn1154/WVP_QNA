"""
Financial document model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, func, Index

from app.models.base import Base


class FinancialDoc(Base):
    __tablename__ = "financial_docs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    doc_type = Column(String(50))  # '사업보고서', '반기보고서', '분기보고서'
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_financial_docs_company_year', 'company_name', 'year'),
    )