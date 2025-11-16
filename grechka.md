# Phase 2: Intelligence Layer - Implementation Guide

## Context from Phase 1

### What We Built in Phase 1
- ✅ Autonomous morning briefing system that runs at 6 AM
- ✅ Telegram bot with basic commands and group support
- ✅ Profile setup feature in Telegram
- ✅ WebApp integration inside Telegram
- ✅ Basic LLM integration (needs replacement)
- ✅ Real-time dashboard with WebSocket
- ✅ Memory system foundation

### Current Issues to Fix
- ❌ /start command not functioning
- ❌ DeepSeek API requires payment
- ❌ No authentication system
- ❌ Limited intelligence features

## Phase 2 Objectives

### Primary Goals
1. **Fix Critical Issues**: Authentication, free LLM, /start command
2. **Add Intelligence**: Competitor monitoring, legal compliance, financial prediction
3. **Improve Autonomy**: Smarter decision-making based on patterns
4. **Enhance Security**: Proper user authentication and data isolation

### Value Addition
Transform the basic autonomous agent into a predictive intelligence system that prevents problems 3 days before they occur and responds to market changes in real-time.

## Priority 1: Critical Fixes (Day 1)

### Task 1.1: Implement Authentication System

**Problem**: Currently no authentication between Telegram, WebApp, and API

**Solution Options**:
1. **Telegram WebApp Auth** (Recommended)
   - Use Telegram's built-in authentication
   - Validate initData hash from Telegram
   - Generate JWT tokens for API access

2. **Implementation Steps**:
   - Backend: Create auth middleware that validates Telegram initData
   - Backend: Generate and validate JWT tokens
   - Frontend: Store JWT in localStorage/cookies
   - Frontend: Add auth headers to all API requests
   - Database: Link all data to authenticated user_id

**Authentication Flow**:
```
1. User opens bot → Telegram provides user data
2. Bot sends user data to backend
3. Backend validates Telegram signature
4. Backend generates JWT token
5. Frontend receives and stores token
6. All subsequent requests include token
```

### Task 1.2: Replace with Free LLM API

**Problem**: DeepSeek requires payment

**Free Alternatives**:
1. **OpenRouter Free Models** (Recommended)
   - Create account at openrouter.ai
   - Use free models: Google Gemma, Mistral 7B
   - No credit card required

2. **Together AI**
   - $25 free credits on signup
   - Access to Llama 3.1 70B
   - No credit card for initial credits

3. **Groq Cloud**
   - Free tier with generous limits
   - Very fast inference
   - Access to Llama models

**Implementation Priority**:
```
Primary: OpenRouter with free models
Fallback 1: Together AI (if user has credits)
Fallback 2: Local Ollama for simple tasks
```

### Task 1.3: Fix /start Command

**Problem**: /start command doesn't trigger

**Debugging Steps**:
1. Check webhook registration with Telegram
2. Verify command handler is registered
3. Check for conflicting handlers
4. Ensure proper response is sent

**Expected Behavior**:
```
/start should:
1. Check if user exists in database
2. If new: Start onboarding flow
3. If existing: Show main menu
4. Send welcome message with inline keyboard
```

## Priority 2: Intelligence Features (Days 2-3)

### Task 2.1: Competitor Monitoring System

**What It Does**: Automatically scans competitors every 2 hours

**Backend Developer Tasks**:
1. Create competitor scanning scheduler (runs every 2 hours)
2. Build VK API integration for public pages
3. Build Telegram channel scanner (using public API)
4. Create price/promotion extractor using LLM
5. Build counter-strategy generator
6. Add competitor_actions table to database
7. Create notification system for significant changes

**Frontend Developer Tasks**:
1. Build competitor dashboard page
2. Create competitor comparison cards
3. Add strategy selection interface
4. Build price change visualization
5. Create competitive analysis charts
6. Add competitor management settings

**Data Sources to Integrate**:
- VK public pages API
- Telegram public channels
- 2GIS business listings
- Yandex.Maps reviews API

### Task 2.2: Legal Compliance Scanner

**What It Does**: Monitors new regulations daily

**Backend Developer Tasks**:
1. Create RSS feed parser for government sites
2. Build relevance analyzer using LLM
3. Create compliance alert system
4. Build document template updater
5. Add legal_updates table to database
6. Create deadline tracker

**Frontend Developer Tasks**:
1. Build compliance status dashboard
2. Create traffic light indicator (red/yellow/green)
3. Add action items list with deadlines
4. Build document template manager
5. Create compliance history view

**Data Sources to Monitor**:
- government publication feeds
- consultant.ru RSS
- industry association updates
- regional regulation feeds

### Task 2.3: Financial Predictor

**What It Does**: Predicts cash flow 7 days ahead

**Backend Developer Tasks**:
1. Create financial data aggregator
2. Build prediction algorithm (start with moving averages)
3. Create risk assessment system
4. Build solution generator for problems
5. Add cash_flow_predictions table
6. Create alert system for high-risk days

**Frontend Developer Tasks**:
1. Build cash flow visualization chart
2. Create risk indicator component
3. Add solution cards with actions
4. Build financial calendar view
5. Create expense optimizer interface

### Task 2.4: Market Trend Detector

**What It Does**: Identifies opportunities from market signals

**Backend Developer Tasks**:
1. Create keyword monitoring system
2. Build trend identification algorithm
3. Create viral opportunity detector
4. Build seasonal pattern analyzer
5. Add market_trends table to database

**Frontend Developer Tasks**:
1. Build trend dashboard
2. Create opportunity cards
3. Add trend visualization graphs
4. Build action recommendation interface

## Task Division for 2 Developers

### Developer A: Backend & Intelligence
**Day 1 (Critical Fixes)**
- Morning: Implement JWT authentication system (3 hours)
- Morning: Set up OpenRouter API integration (1 hour)
- Afternoon: Fix /start command handler (2 hours)
- Afternoon: Test authentication flow end-to-end (2 hours)

**Day 2 (Competitor & Legal)**
- Morning: Build competitor scanning system (2 hours)
- Morning: Implement VK/Telegram scrapers (2 hours)
- Afternoon: Create legal compliance scanner (2 hours)
- Afternoon: Build RSS feed processors (2 hours)

**Day 3 (Financial & Trends)**
- Morning: Build financial prediction system (3 hours)
- Morning: Create alert mechanisms (1 hour)
- Afternoon: Implement trend detection (2 hours)
- Afternoon: Integration testing (2 hours)

### Developer B: Frontend & UI
**Day 1 (Critical Fixes)**
- Morning: Add authentication to frontend (3 hours)
- Morning: Implement token management (1 hour)
- Afternoon: Create auth UI components (2 hours)
- Afternoon: Test auth flow with backend (2 hours)

**Day 2 (Intelligence Dashboards)**
- Morning: Build competitor dashboard (2 hours)
- Morning: Create compliance status view (2 hours)
- Afternoon: Design financial predictor UI (2 hours)
- Afternoon: Build alert components (2 hours)

**Day 3 (Integration & Polish)**
- Morning: Create trend visualization (2 hours)
- Morning: Build settings pages (2 hours)
- Afternoon: Connect all dashboards to API (2 hours)
- Afternoon: UI polish and testing (2 hours)

## Database Schema Additions for Phase 2
```sql
-- Add to existing schema

-- Competitors tracking
CREATE TABLE competitors (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    vk_group_id VARCHAR(100),
    telegram_channel VARCHAR(100),
    website_url TEXT,
    last_scanned TIMESTAMP
);

CREATE TABLE competitor_actions (
    id UUID PRIMARY KEY,
    competitor_id UUID REFERENCES competitors(id),
    action_type VARCHAR(50), -- price_change, new_promotion, new_product
    details JSONB,
    detected_at TIMESTAMP,
    our_response JSONB
);

-- Legal compliance
CREATE TABLE legal_updates (
    id UUID PRIMARY KEY,
    title TEXT,
    source VARCHAR(255),
    relevance_score FLOAT,
    impact_description TEXT,
    published_date DATE,
    deadline DATE
);

CREATE TABLE compliance_alerts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    legal_update_id UUID REFERENCES legal_updates(id),
    status VARCHAR(50), -- pending, completed, overdue
    action_required TEXT,
    due_date DATE
);

-- Financial predictions
CREATE TABLE cash_flow_predictions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    prediction_date DATE,
    predicted_balance DECIMAL,
    confidence_score FLOAT,
    risk_level VARCHAR(20), -- low, medium, high
    created_at TIMESTAMP
);

-- Market trends
CREATE TABLE market_trends (
    id UUID PRIMARY KEY,
    trend_name VARCHAR(255),
    category VARCHAR(100),
    strength_score FLOAT,
    detected_at TIMESTAMP,
    relevant_keywords TEXT[]
);
```

## API Endpoints for Phase 2
```
Authentication:
POST /api/v1/auth/telegram/validate   # Validate Telegram auth
POST /api/v1/auth/token/refresh       # Refresh JWT token
GET  /api/v1/auth/me                  # Get current user

Competitor Intelligence:
GET  /api/v1/competitors              # List competitors
POST /api/v1/competitors              # Add competitor
GET  /api/v1/competitors/{id}/actions # Recent actions
POST /api/v1/competitors/scan         # Force scan
GET  /api/v1/competitors/insights     # Analysis

Legal Compliance:
GET  /api/v1/compliance/status        # Overall status
GET  /api/v1/compliance/alerts        # Active alerts
POST /api/v1/compliance/complete/{id} # Mark completed
GET  /api/v1/compliance/updates       # Recent law changes

Financial:
GET  /api/v1/financial/forecast       # 7-day forecast
GET  /api/v1/financial/risks          # Risk alerts
GET  /api/v1/financial/solutions      # Problem solutions

Trends:
GET  /api/v1/trends/current           # Active trends
GET  /api/v1/trends/opportunities     # Opportunities
```

## Environment Variables for Phase 2
```env
# Authentication
JWT_SECRET_KEY=your_random_secret_key_here
JWT_EXPIRE_MINUTES=10080  # 7 days

# Free LLM Options
OPENROUTER_API_KEY=your_free_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_FREE_MODEL=google/gemma-7b-it:free

# Alternative free options
TOGETHER_API_KEY=your_25_dollar_credit_key
GROQ_API_KEY=your_free_groq_key

# External APIs
VK_SERVICE_TOKEN=your_vk_service_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Scanning intervals (minutes)
COMPETITOR_SCAN_INTERVAL=120
LEGAL_SCAN_INTERVAL=1440
FINANCIAL_PREDICT_INTERVAL=360
```

## Testing Checklist for Phase 2

### Authentication
- [ ] Telegram auth validates correctly
- [ ] JWT tokens generated and validated
- [ ] Protected endpoints require auth
- [ ] Token refresh works
- [ ] User data properly isolated

### Intelligence Features
- [ ] Competitors scanned every 2 hours
- [ ] Price changes detected
- [ ] Legal updates parsed daily
- [ ] Relevant laws filtered correctly
- [ ] Cash flow predicted for 7 days
- [ ] Risk alerts sent on time
- [ ] Trends identified from data

### UI/UX
- [ ] All dashboards load with auth
- [ ] Real-time updates work
- [ ] Mobile responsive
- [ ] Telegram WebApp compatible

## Success Metrics for Phase 2

- Competitor changes detected within 2 hours
- Legal compliance alerts 7 days before deadline
- Cash flow predictions 85% accurate
- 3+ market trends identified daily
- Zero authentication failures
- Free LLM costs: $0

## Demo Additions for Phase 2

1. **Show competitor detection**: "Your competitor just lowered prices 15%. Here's our recommended response..."
2. **Prevent legal issue**: "New regulation takes effect in 7 days. Your contracts have been updated."
3. **Predict cash shortage**: "Cash flow warning for Thursday. Top 3 solutions ready."
4. **Spot opportunity**: "Trending: Matcha Monday up 400%. Your competitors haven't noticed yet."
