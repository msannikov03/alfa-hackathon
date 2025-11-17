# Alfa Business Assistant

Autonomous AI business assistant with Telegram bot, real-time dashboard, and automated decision-making.

## Features

### Core Features
- **🤖 Telegram Bot** - Two modes: Demo (pre-loaded sample data) and Live (your own business)
- **📊 Real-time Dashboard** - WebSocket-powered live updates and metrics
- **🧠 Autonomous Actions** - AI makes decisions within configurable thresholds
- **📋 Morning Briefings** - Automated daily summaries at 6 AM
- **✅ Approval System** - Review and approve/decline AI actions
- **💾 Memory & Learning** - ChromaDB vector store for pattern recognition

### Intelligence Features (Phase 2)
- **🎯 Competitor Monitoring**
  - Automatic scanning of websites and Telegram channels every 2 hours
  - Add/manage competitors via bot or dashboard
  - AI identifies price changes, promotions, new products
  - Detailed error handling for blocked/unavailable sites
- **⚖️ Legal Compliance Scanner**
  - Daily RSS feed monitoring for relevant regulations
  - Set business context for personalized legal alerts
  - Automatic compliance deadlines and action items
  - Full integration in bot and dashboard
- **💰 Financial Predictor**
  - AI-powered 7-day cash flow forecasting
  - CSV upload via bot or dashboard
  - Automatic column detection with LLM
  - Risk analysis and recommendations
- **📈 Strategic Trends**
  - Cross-domain analysis (finance + legal + competitors)
  - Identifies opportunities, threats, and efficiency improvements
  - Actionable recommendations with importance scoring
  - Available via bot command and dashboard

## Quick Start

### 1. Get API Keys

**LLM7.io** - Free LLM access:
- Go to https://token.llm7.io
- Get your free API token (no payment required)

**Telegram Bot Token**:
- Open Telegram, search @BotFather
- Send `/newbot` and follow instructions
- Copy the token

### 2. Configure & Start

```bash
# Clone repo
git clone https://github.com/msannikov03/alfa-hackathon.git
cd alfa-hackathon

# Add API keys to .env
nano .env
# Set LLM7_API_KEY and TELEGRAM_BOT_TOKEN

# Start everything
./start.sh
```

### 3. Access

**Dashboard:** http://localhost:3000/login
- Demo: `demo_admin` / `demo123` (sample business data)
- Admin: `admin` / `admin123` (clean slate)

**Telegram Bot:**
- Open Telegram, find your bot
- Send `/start`
- Choose **Demo Mode** to see sample data
- Or **Live Mode** to create your own business

## Bot Commands

### Core Commands
```
/start        - Choose Demo or Live mode
/briefing     - Get today's business briefing
/stats        - View statistics and metrics
/approve      - Check pending approvals
/setup        - Configure your business profile
/setpassword  - Set password for dashboard access
/changemode   - Switch between Demo/Live modes
/help         - Show all commands
```

### Intelligence Features
```
🎯 Competitor Monitoring:
/competitors      - List all tracked competitors
/addcompetitor    - Add new competitor (wizard)
/scancompetitors  - Scan all competitors now

⚖️ Legal & Compliance:
/legal        - View recent legal updates
/setcontext   - Set business context for monitoring
/compliance   - View compliance alerts and deadlines

💰 Financial Analytics:
/forecast     - View 7-day cash flow forecast
📎 Send CSV   - Upload bank statement for analysis

📈 Strategic Intelligence:
/trends       - View cross-domain strategic trends
```

## Demo Mode - Rich Sample Data

**Why Demo Data?** Setting up a complete business intelligence system takes time. Our demo mode lets you see the full value immediately - every feature, every insight, working out of the box.

Pre-loaded with complete **Demo Coffee Shop** business:

**Core Features:**
- ✅ 6 autonomous actions (inventory, staffing, marketing, pricing)
- ✅ 3 pending approvals to test workflow
- ✅ Full business context (₽75K/day revenue, 150 customers, 8 staff)
- ✅ Today's AI-generated briefing with actionable insights
- ✅ 30 days of financial transaction history

**Phase 2 Intelligence:**
- ✅ 4 real competitors (Coffee House, Starbucks, Шоколадница, Кофемания)
- ✅ 8 competitor actions tracked (price changes, promotions, new products)
- ✅ 4 legal updates with impact analysis (VAT increase, online cash register rules, etc.)
- ✅ 3 compliance alerts with due dates (urgent tasks you need to complete)
- ✅ 7-day cash flow forecast (₽450K → ₽900K+ projected)
- ✅ 5 strategic market trends (opportunities, threats, efficiency improvements)
- ✅ Complete briefing report ready to view

**Perfect For:**
- 🎯 Demos and presentations - show real value instantly
- 🧪 Testing all features without manual data entry
- 📊 Understanding what the system can do for your business
- 🚀 Getting started quickly in production (just switch to Live mode when ready)

All data is realistic, interconnected, and demonstrates the full power of the AI assistant.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind v4 |
| Backend | FastAPI, Python 3.11, SQLAlchemy (async) |
| Database | PostgreSQL 15 |
| LLM | LLM7.io API (Free gateway to multiple models) |
| Vector Store | ChromaDB with embeddings |
| Bot | python-telegram-bot 21.7 |
| Real-time | WebSocket |
| Deployment | Docker Compose |

## Project Structure

```
alfa-hackathon/
├── backend/
│   ├── seed_demo_data.py          # Creates demo business data
│   ├── app/
│   │   ├── api/                   # REST API endpoints
│   │   ├── telegram/bot.py        # Telegram bot with demo/live modes
│   │   ├── models/                # Database models
│   │   ├── services/              # LLM, memory services
│   │   └── agents/                # Briefing agent
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── dashboard/page.tsx     # Real-time dashboard
│   │   ├── login/page.tsx         # Login page
│   │   └── tg-app/page.tsx        # Telegram Mini App
│   └── components/
├── .env                           # Your config (gitignored)
├── .env.example                   # Template
├── docker-compose.yml             # Services config
├── start.sh                       # Quick start script
├── README.md                      # This file
└── PROJECT_CONTEXT.md             # For LLMs/developers
```

## Development

```bash
# Start services
./start.sh

# View logs
docker compose logs -f backend

# Restart after code changes
docker compose restart backend

# Stop everything
docker compose down

# Fresh start (deletes data)
docker compose down -v
./start.sh
```

## Environment Variables

Key variables in `.env`:

```env
# Required
LLM7_API_KEY=your_token_here...        # Free token from https://token.llm7.io
TELEGRAM_BOT_TOKEN=123456:ABC...       # From @BotFather

# Database (use defaults for Docker)
POSTGRES_PASSWORD=alfa_password_change_me

# Webapp URL
TELEGRAM_WEBAPP_URL=http://localhost:3000/tg-app  # Local
# TELEGRAM_WEBAPP_URL=https://yourdomain.com/tg-app  # Production

# Features
ENABLE_AUTONOMOUS_ACTIONS=true
MORNING_BRIEFING_TIME=06:00
DECISION_THRESHOLD_AMOUNT=10000        # Auto-approve under ₽10K
```

## API Endpoints

**Base URL:** http://localhost:8000

**Interactive docs:** http://localhost:8000/docs

Key endpoints:
- `GET /api/v1/briefing/today?user_id=1` - Today's briefing
- `GET /api/v1/actions/recent?user_id=1` - Recent actions
- `GET /api/v1/actions/pending?user_id=1` - Pending approvals
- `POST /api/v1/actions/approve/{action_id}` - Approve action
- `GET /api/v1/metrics/performance?user_id=1` - Metrics
- `WS /ws?user_id=1` - WebSocket for real-time updates

## Troubleshooting

**Bot not responding:**
```bash
docker compose logs backend | grep "Telegram"
docker compose restart backend
```

**Seed script failed:**
```bash
docker exec alfa_backend python seed_demo_data.py
```

**Database issues:**
```bash
# Reset database
docker compose down -v
./start.sh
```

## Deployment

See `DEPLOYMENT.md` for complete Raspberry Pi deployment with:
- Cloudflare Tunnel setup (bypass firewall)
- CI/CD auto-deploy on git push
- Production configuration

## License

MIT License

---

**Built for Alfa Hackathon 2025** - Autonomous AI that works while you sleep 🌙
