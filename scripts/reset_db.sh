#!/bin/bash
# Reset database - WARNING: This will delete all data!

echo "WARNING: This will delete all data in the database!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Remove existing database
echo "Removing existing database..."
rm -f data/portfolio_qa.db

# Activate virtual environment
source venv/bin/activate

# Run migrations
echo "Creating fresh database..."
alembic upgrade head

echo "Database reset complete!"

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