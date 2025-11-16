#!/bin/bash
set -e

echo "Running seed script to ensure demo data exists..."
python seed_demo_data.py || echo "Seed script failed, continuing anyway..."

echo "Starting server..."
exec "$@"
