# Alfa Business Assistant 🤖

> Autonomous AI-powered business assistant with Telegram integration for Russian SMB owners

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Phase 1](https://img.shields.io/badge/phase%201-complete-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

An intelligent business assistant that works autonomously, makes decisions within configured thresholds, and only escalates critical matters. Features morning briefings, Telegram bot integration, real-time dashboard, and AI-powered decision making.

---

## ✨ Features

- **🌅 Morning Briefings** - Automated daily summaries at 6 AM
- **🤖 Autonomous Actions** - AI makes decisions within thresholds
- **💬 Telegram Bot** - Full-featured bot with inline keyboards and group support
- **📱 Telegram Mini App** - Rich WebApp interface inside Telegram
- **📊 Real-time Dashboard** - WebSocket-powered live updates
- **🧠 Pattern Recognition** - ChromaDB-powered memory and learning
- **💼 Business Context** - Personalized AI based on your business data

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (latest)
- **Git**
- **API Keys** (see setup instructions below)

### 1. Clone Repository

```bash
git clone https://github.com/msannikov03/alfa-hackathon.git
cd alfa-hackathon
```

### 2. Obtain Required API Keys

You need **TWO** API keys (both free):

#### A) DeepSeek API Key (FREE)
**Purpose:** LLM for business intelligence
**Free Tier:** 5 million tokens (~$8.40 value, valid 30 days)

1. Visit https://platform.deepseek.com/
2. Sign up or log in
3. Go to **API Keys** section
4. Click **Create API Key**
5. **Copy the key** - you'll need it in step 3

#### B) Telegram Bot Token (FREE)
**Purpose:** Telegram bot and Mini App

1. Open **Telegram**
2. Search for **@BotFather**
3. Send `/newbot` command
4. Follow instructions to create your bot
5. **Copy the token** - you'll need it in step 3

### 3. Configure Environment

The `.env` file has been created for you. Edit it with your API keys:

```bash
nano .env
# or use any text editor
```

**REQUIRED:** Replace these two lines:
```env
DEEPSEEK_API_KEY=PASTE_YOUR_DEEPSEEK_API_KEY_HERE
TELEGRAM_BOT_TOKEN=PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE
```

All other variables are pre-configured and ready to use.

### 4. Build & Start

```bash
# Build all services
docker compose build

# Start in detached mode
docker compose up -d

# Check that everything is running
docker compose ps
```

**Wait 10-15 seconds** for PostgreSQL to initialize, then check logs:

```bash
# View backend logs
docker compose logs -f backend

# Look for these success messages:
# ✓ "Starting Alfa Business Assistant..."
# ✓ "Scheduler started - Morning briefings at 06:00"
# ✓ "Telegram bot started with enhanced features"
```

### 5. Access the Application

- **Frontend Dashboard:** http://localhost:3000
- **Real-time Dashboard:** http://localhost:3000/dashboard
- **Telegram Mini App:** http://localhost:3000/tg-app (or via Telegram bot)
- **Backend API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 6. Test Telegram Bot

1. Open Telegram and search for your bot
2. Send `/start` command
3. Try other commands:
   - `/briefing` - Get morning briefing
   - `/stats` - View statistics
   - `/approve` - Check pending approvals
   - `/help` - See all commands

---

## 📖 Usage Guide

### Telegram Bot Commands

```
/start    - Initialize user and business profile
/briefing - Get latest morning briefing
/stats    - Today's performance metrics
/approve  - Show pending approvals
/help     - Show available features
```

### API Endpoints

**Base URL:** `http://localhost:8000`

#### Briefing
- `GET /api/v1/briefing/today?user_id=1`
- `POST /api/v1/briefing/generate?user_id=1`
- `GET /api/v1/briefing/history?user_id=1&days=7`

#### Actions
- `GET /api/v1/actions/recent?user_id=1&limit=20`
- `GET /api/v1/actions/pending?user_id=1`
- `POST /api/v1/actions/approve/{action_id}`
- `POST /api/v1/actions/decline/{action_id}`

#### Metrics
- `GET /api/v1/metrics/savings?user_id=1`
- `GET /api/v1/metrics/performance?user_id=1`

**Full API documentation:** http://localhost:8000/docs

### WebSocket (Real-time Updates)

```javascript
const ws = new WebSocket("ws://localhost:8000/ws?user_id=1");

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // message.type: "action_taken", "approval_needed", "metric_update", "briefing_ready"
  console.log(message);
};
```

---

## 🔧 Development

### Docker Commands (Recommended)

```bash
# Start all services
docker compose up -d

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# Restart a service
docker compose restart backend

# Rebuild after code changes
docker compose build backend
docker compose restart backend

# Stop everything
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```

### Local Development (Without Docker)

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Access at http://localhost:8000
```

**Database (still needs Docker):**
```bash
docker compose up postgres -d
```

---

## 📊 Database Schema

The database is **automatically created** on first startup. No manual setup needed!

**Tables:**
- `users` - User accounts and business profiles
- `briefings` - Daily morning briefings
- `autonomous_actions` - AI action tracking
- `learned_patterns` - Pattern recognition data
- `decisions` - Decision history for learning
- `business_contexts` - Business information and thresholds

To reset the database:
```bash
docker compose down -v
docker compose up -d
```

---

## 🛠 Configuration

### Environment Variables

All configuration is in `.env`. Key variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | - | ✅ |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | - | ✅ |
| `POSTGRES_PASSWORD` | Database password | `alfa_password_change_me` | ❌ |
| `MORNING_BRIEFING_TIME` | Briefing time (HH:MM) | `06:00` | ❌ |
| `DECISION_THRESHOLD_AMOUNT` | Auto-approve threshold (₽) | `10000` | ❌ |
| `ENABLE_AUTONOMOUS_ACTIONS` | Enable autonomous features | `true` | ❌ |

### Customizing Decision Thresholds

Edit in `.env`:
```env
DECISION_THRESHOLD_AMOUNT=10000  # Actions under ₽10,000 auto-approved
```

Or configure per-user via API (coming in Phase 2).

---

## 🐛 Troubleshooting

### Backend won't start

**Issue:** "Connection to database failed"
```bash
# Check PostgreSQL is healthy
docker compose ps

# Wait 10-15 seconds for initialization, then:
docker compose restart backend
```

### DeepSeek API errors

**Issue:** "Error calling LLM: API key is invalid"
- Verify `DEEPSEEK_API_KEY` in `.env` is correct
- Check you have free tier remaining: https://platform.deepseek.com/usage

### Telegram bot not responding

**Issue:** Bot doesn't respond to messages
```bash
# Check bot is started
docker compose logs backend | grep "Telegram bot started"

# Verify token is correct
grep TELEGRAM_BOT_TOKEN .env
```

### WebSocket connection failed

**Issue:** Dashboard shows "Connecting..." forever
- Ensure backend is running: `docker compose ps backend`
- Check browser console for errors
- Try refreshing the page

### ChromaDB errors

**Issue:** "chromadb.errors.InvalidCollectionException"
```bash
# Delete ChromaDB data and restart
rm -rf backend/chroma_data
docker compose restart backend
```

### Port already in use

**Issue:** "Port 3000 (or 8000) already in use"
```bash
# Find and kill the process
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or change ports in docker-compose.yml
```

---

## 📚 Documentation

- **PROJECT_CONTEXT.md** - Comprehensive technical documentation
- **API Docs** - http://localhost:8000/docs (interactive Swagger UI)
- **instructions.md** - Phase 1 feature specifications

---

## 🏗 Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 16.0.1, React 19, TypeScript, Tailwind CSS v4 |
| Backend | FastAPI 0.115.0, Python 3.11 |
| Database | PostgreSQL 15 with SQLAlchemy (async) |
| LLM | DeepSeek API (OpenAI-compatible) |
| Vector Store | ChromaDB 0.5.20 with embeddings |
| Scheduler | APScheduler 3.10.4 |
| Bot Framework | python-telegram-bot 21.7 |
| Real-time | WebSocket (websockets 14.1) |
| Deployment | Docker & Docker Compose |

---

## 🎯 Project Structure

```
alfa-hackathon/
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── dashboard/          # Real-time dashboard (WebSocket)
│   │   ├── tg-app/             # Telegram Mini App
│   │   └── api/                # API routes
│   └── components/             # Reusable UI components
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/                # API routes & WebSocket
│   │   ├── models/             # Database models (6 tables)
│   │   ├── services/           # LLM, Memory, AI services
│   │   ├── agents/             # Briefing agent
│   │   └── telegram/           # Telegram bot handlers
│   └── requirements.txt        # Python dependencies
│
├── .env                        # Environment configuration (git-ignored)
├── .env.example                # Environment template
├── docker-compose.yml          # Service orchestration
└── README.md                   # This file
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Change `POSTGRES_PASSWORD` to a strong password
- [ ] Generate new `JWT_SECRET`: `openssl rand -hex 32`
- [ ] Set `ENABLE_AUTONOMOUS_ACTIONS=true` (if desired)
- [ ] Configure proper CORS origins in `backend/app/main.py`
- [ ] Set up SSL/HTTPS with reverse proxy (nginx, Caddy)
- [ ] Enable monitoring (Sentry, LogRocket)
- [ ] Configure backups for PostgreSQL
- [ ] Set up rate limiting

### Deploy to Cloud

Compatible with:
- **Railway** - `railway up`
- **Render** - Connect GitHub repo
- **Fly.io** - `fly launch`
- **DigitalOcean App Platform** - Connect GitHub repo
- **AWS ECS** / **Google Cloud Run** - Use Docker images

---

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🆘 Support

**Issues:** https://github.com/msannikov03/alfa-hackathon/issues

**Need API Keys?**
- DeepSeek: https://platform.deepseek.com/
- Telegram Bot: Search @BotFather in Telegram

---

**Built with ❤️ for Alfa Hackathon 2025**

*Autonomous AI that works while you sleep* 🌙
