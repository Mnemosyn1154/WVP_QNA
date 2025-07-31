#!/bin/bash
# Initialize development database with sample data

echo "Initializing development database with sample data..."

# Activate virtual environment
source venv/bin/activate

# Step 1: Reset database (with confirmation)
echo "This will reset the database and add sample data."
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Reset database
echo "Resetting database..."
./scripts/reset_db.sh <<< ""

# Step 2: Seed sample data
echo ""
echo "Seeding sample data..."
python scripts/seed_data.py

echo ""
echo "Development database initialization complete!"
echo ""
echo "You can now start the application with:"
echo "  - Backend: python run_backend.py"
echo "  - Frontend: cd frontend && npm run dev"