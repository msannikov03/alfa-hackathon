#!/bin/bash
set -e

echo "================================"
echo "Production Deployment Script"
echo "================================"
echo ""

# Pull latest code
echo "Pulling latest changes..."
git pull origin main

# Stop current containers
echo "Stopping containers..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# Build fresh images
echo "Building production images..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# Start services
echo "Starting services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services
echo "Waiting for services to start..."
sleep 15

# Check status
echo ""
echo "=== Container Status ==="
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

echo ""
echo "=== Health Checks ==="
echo -n "Backend: "
curl -f http://localhost:8000/health && echo "✓ OK" || echo "✗ FAILED"

echo -n "Frontend: "
curl -f -I http://localhost:3000 && echo "✓ OK" || echo "✗ FAILED"

echo ""
echo "=== Recent Logs ==="
echo "Backend:"
docker logs --tail 10 alfa_backend
echo ""
echo "Frontend:"
docker logs --tail 10 alfa_frontend

echo ""
echo "================================"
echo "Deployment Complete!"
echo "================================"
