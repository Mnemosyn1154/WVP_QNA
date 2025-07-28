#!/bin/bash
cd /Users/mnemosyn1154/QnA_Agent
source venv/bin/activate

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8081