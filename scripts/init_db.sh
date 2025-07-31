#!/bin/bash
# Initialize database with Alembic migrations

echo "Initializing database..."

# Activate virtual environment
source venv/bin/activate

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "Database initialization complete!"

# Show current database status
echo ""
echo "Current database tables:"
python -c "
from sqlalchemy import create_engine, inspect
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
tables = inspector.get_table_names()

for table in sorted(tables):
    if table != 'alembic_version':
        print(f'  ✓ {table}')
"