#!/bin/bash
echo "================================"
echo "ALFA HACKATHON DEBUG INFO"
echo "================================"
echo ""

echo "=== 1. PROJECT STRUCTURE ==="
ls -la ~/alfa-hackathon/ | grep -E "docker-compose|\.env|frontend|backend"
echo ""

echo "=== 2. .ENV FILE CONTENT (SENSITIVE PARTS HIDDEN) ==="
cat .env | grep -v "PASSWORD\|SECRET\|TOKEN\|KEY" | grep -E "NEXT_PUBLIC|TELEGRAM_WEBAPP|API_URL"
echo ""

echo "=== 3. DOCKER-COMPOSE.YML (FRONTEND ENV SECTION) ==="
grep -A 20 "frontend:" docker-compose.yml | head -30
echo ""

echo "=== 4. CONTAINER STATUS ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== 5. FRONTEND ENV VARS IN CONTAINER ==="
docker exec alfa_frontend env | grep -E "NEXT_PUBLIC|NODE_ENV|API"
echo ""

echo "=== 6. BACKEND ENV VARS IN CONTAINER ==="
docker exec alfa_backend env | grep -E "DATABASE_URL|CORS|TELEGRAM" | grep -v "PASSWORD\|SECRET\|TOKEN"
echo ""

echo "=== 7. FRONTEND LOGS (LAST 30 LINES) ==="
docker logs --tail 30 alfa_frontend
echo ""

echo "=== 8. BACKEND LOGS (LAST 30 LINES) ==="
docker logs --tail 30 alfa_backend
echo ""

echo "=== 9. TEST LOCAL ACCESS ==="
echo "Frontend (port 3000):"
curl -s -I http://localhost:3000 | head -5
echo ""
echo "Backend (port 8000):"
curl -s http://localhost:8000/health
echo ""

echo "=== 10. CHECK IF .ENV IS BEING LOADED ==="
docker exec alfa_frontend sh -c 'ls -la /app/.env* 2>/dev/null || echo "No .env files found in container"'
echo ""

echo "=== 11. FRONTEND PACKAGE.JSON (CHECK BUILD SCRIPT) ==="
docker exec alfa_frontend cat /app/package.json | grep -A 5 '"scripts"'
echo ""

echo "=== 12. CHECK NEXT.JS CONFIG ==="
docker exec alfa_frontend cat /app/next.config.js 2>/dev/null || docker exec alfa_frontend cat /app/next.config.mjs 2>/dev/null || echo "No next.config found"
echo ""

echo "================================"
echo "DEBUG INFO COLLECTION COMPLETE"
echo "================================"
