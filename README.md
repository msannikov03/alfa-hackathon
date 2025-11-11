# Alfa Business Assistant

AI-powered business assistant with Telegram integration for managing your business.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Setup

```bash
# Clone
git clone https://github.com/msannikov03/alfa-hackathon.git
cd alfa-hackathon

# Build & Start
docker compose build
docker compose up -d

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

No .env file needed for development - works with sensible defaults.

---

## Configuration (Optional)

For production, create and edit `.env`:

```bash
cp .env.example .env
nano .env
```

Update these values:
- `POSTGRES_PASSWORD` - Database password
- `JWT_SECRET` - JWT secret key
- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `TELEGRAM_BOT_NAME` - Your bot username

Then restart:
```bash
docker compose down
docker compose up --build -d
```

---

## Development

### Docker (Recommended)
```bash
docker compose up -d          # Start all services
docker compose logs -f        # View logs
docker compose down           # Stop
```

### Local Development
**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Database:**
```bash
docker compose up postgres -d
```

---

## Commands

### Build
```bash
docker compose build              # All services
docker compose build frontend     # Specific service
docker compose build --no-cache   # Clean build
```

### Service Management
```bash
docker compose up -d              # Start
docker compose ps                 # Status
docker compose restart backend    # Restart service
docker compose down -v            # Stop & remove data
```

### Logs
```bash
docker compose logs -f            # All services
docker compose logs -f backend    # Specific service
docker compose logs --tail 50     # Last 50 lines
```

---

## Tech Stack

**Frontend:** Next.js 14, TypeScript, Tailwind CSS v4
**Backend:** FastAPI, Python 3.11, PostgreSQL 15
**Infrastructure:** Docker, GitHub Actions

---

## Project Structure

```
├── frontend/          # Next.js app
│   ├── app/          # Pages & routes
│   ├── components/   # UI components
│   └── lib/          # API client & utils
├── backend/          # FastAPI app
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   └── telegram/ # Bot handlers
│   └── requirements.txt
├── .env.example      # Environment template
└── docker-compose.yml
```

See `PROJECT_CONTEXT.md` for detailed technical documentation.

---

## License

MIT License
