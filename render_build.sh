#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r apps/api/requirements.txt

# Run migrations
# We need to set PYTHONPATH so alembic can find 'apps' module
export PYTHONPATH=$PYTHONPATH:.
python -m alembic -c apps/api/alembic.ini upgrade head
