-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- News metadata table
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    content_url TEXT,
    source VARCHAR(100),
    published_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for news table
CREATE INDEX idx_news_company_date ON news (company_name, published_date DESC);

-- Financial documents index table
CREATE TABLE IF NOT EXISTS financial_docs (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    doc_type VARCHAR(50), -- '사업보고서', '반기보고서', '분기보고서'
    year INTEGER NOT NULL,
    quarter INTEGER,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for financial_docs table
CREATE INDEX idx_financial_docs_company_year ON financial_docs (company_name, year DESC);

-- Users table (for future extensibility)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    password_hash TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Chat history table (optional)
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    question TEXT NOT NULL,
    answer TEXT,
    context JSONB, -- stored search document info
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for chat_history
CREATE INDEX idx_chat_history_user_created ON chat_history (user_id, created_at DESC);