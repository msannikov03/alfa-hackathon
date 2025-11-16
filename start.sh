#!/bin/bash
set -e

echo "🚀 Alfa Business Assistant - Starting..."

# Check .env exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Created .env file. Add your API keys and run again."
    exit 1
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker not running"
    exit 1
fi

# Check API keys
if grep -q "your_llm7_api_key_here" .env || grep -q "your_telegram_bot_token_here" .env; then
    echo "⚠️  Add API keys to .env file"
    echo "   Get from: https://token.llm7.io and @BotFather"
    exit 1
fi

# Stop existing containers
docker compose down 2>/dev/null || true

# Check if images exist
if docker images | grep -q "alfa-hackathon-backend" && docker images | grep -q "alfa-hackathon-frontend"; then
    echo "✓ Using existing images"
    docker compose up -d
else
    echo "Building images (first time)..."
    docker compose build || {
        echo "⚠️  Build failed (network issue?). Retrying without cache..."
        sleep 3
        docker compose build --no-cache || {
            echo "❌ Build failed. Check your internet connection."
            echo "   If images exist, run: docker compose up -d"
            exit 1
        }
    }
    docker compose up -d
fi

echo "⏳ Waiting for services..."
sleep 15

# Seed data
echo "🌱 Creating demo data..."
docker exec alfa_backend python seed_demo_data.py 2>/dev/null || {
    sleep 5
    docker exec alfa_backend python seed_demo_data.py 2>/dev/null || true
}

echo ""
echo "✅ Running!"
echo ""
echo "URLs:"
echo "  Dashboard: http://localhost:3000/login"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Login:"
echo "  demo_admin / demo123 (sample data)"
echo "  admin / admin123 (clean slate)"
echo ""
echo "Telegram: /start → Choose Demo Mode"
echo ""
echo "Commands:"
echo "  docker compose logs -f    # View logs"
echo "  docker compose down       # Stop"
echo ""
