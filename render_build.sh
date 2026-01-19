#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r apps/api/requirements.txt

# Run migrations and seed data
# Add current directory (root) to PYTHONPATH so 'apps.api...' imports work
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Change to apps/api directory so alembic finds 'script_location = alembic' correctly
cd apps/api
python -m alembic upgrade head
python seed.py
