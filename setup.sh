#!/bin/bash
# Setup benchmark environment
# Run this once before benchmarking

set -e

cd "$(dirname "$0")"

echo "=== Framework Benchmark Setup ==="
echo ""

# Install dependencies with uv
echo "1. Installing dependencies with uv..."
uv sync

# Run Django migrations
echo ""
echo "2. Setting up Django database..."
uv run python manage.py migrate --run-syncdb

# Seed Django database
echo ""
echo "3. Seeding Django database with 10 users..."
uv run python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_project.settings'

import django
django.setup()

from django_project.users.models import BenchmarkUser

if BenchmarkUser.objects.count() < 10:
    users = [
        BenchmarkUser(
            username=f'user{i:02d}',
            email=f'user{i:02d}@example.com',
            first_name=f'First{i}',
            last_name=f'Last{i}',
        )
        for i in range(10)
    ]
    BenchmarkUser.objects.bulk_create(users, ignore_conflicts=True)
    print(f'Created {len(users)} users')
else:
    print(f'Already have {BenchmarkUser.objects.count()} users')
"

# Setup SQLite database for FastAPI/Litestar
echo ""
echo "4. Setting up SQLAlchemy database..."
uv run python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.models import Base, User

engine = create_engine('sqlite:///./benchmark.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if session.query(User).count() < 10:
    users = [
        User(
            username=f'user{i:02d}',
            email=f'user{i:02d}@example.com',
            first_name=f'First{i}',
            last_name=f'Last{i}',
        )
        for i in range(10)
    ]
    session.add_all(users)
    session.commit()
    print(f'Created {len(users)} users')
else:
    print(f'Already have {session.query(User).count()} users')
session.close()
"

# Make run scripts executable
chmod +x run_*.sh

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run benchmarks:"
echo ""
echo "1. Start servers in separate terminals:"
echo "   ./run_fastapi.sh   # Port 8001"
echo "   ./run_litestar.sh  # Port 8002"
echo "   ./run_ninja.sh     # Port 8003"
echo "   ./run_bolt.sh      # Port 8004"
echo ""
echo "2. Run benchmark:"
echo "   uv run python bench.py"
echo ""
echo "Or use the all-in-one script:"
echo "   ./run_all.sh"
