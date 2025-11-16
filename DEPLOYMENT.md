# Production Deployment Guide

## Quick Start - Production Deployment

This guide covers deploying to production using Docker Compose with production overrides.

### Prerequisites
- Docker and Docker Compose installed
- Cloudflare Tunnel configured (optional, for external access)
- Environment variables configured in `.env`

### Initial Setup

1. **Clone repository:**
```bash
git clone https://github.com/msannikov03/alfa-hackathon.git
cd alfa-hackathon
```

2. **Create .env file:**
```bash
cp .env.example .env
nano .env
```

Update these critical values:
- `NEXT_PUBLIC_API_URL=https://alfa.businesslion.me`
- `TELEGRAM_WEBAPP_URL=https://alfa.businesslion.me/tg-app`
- `API_URL=https://alfa.businesslion.me`
- `CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,https://alfa.businesslion.me`
- `POSTGRES_PASSWORD=<generate strong password>`
- `JWT_SECRET=<generate with: openssl rand -hex 32>`

3. **Deploy:**
```bash
chmod +x deploy-production.sh
./deploy-production.sh
```

### Updating

To deploy updates:
```bash
./deploy-production.sh
```

Or manually:
```bash
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Architecture

- **Development:** Uses `docker-compose.yml` only
- **Production:** Uses both `docker-compose.yml` + `docker-compose.prod.yml` (override)

The production override:
- Runs backend with multiple workers (not reload)
- Runs frontend with production build (not dev server)
- Removes volume mounts (uses built images)
- Sets restart policies

---

# Raspberry Pi Deployment with Auto-Deploy

Deploy to Raspberry Pi with Cloudflare Tunnel and automatic deployment on git push.

## Prerequisites

- Raspberry Pi 4 (4GB+ RAM)
- Raspberry Pi OS (64-bit)
- Cloudflare account (free tier works)
- GitHub repository access

---

## Part 1: Raspberry Pi Setup

### 1. Prepare Raspberry Pi

```bash
# SSH into Pi
ssh pi@<your-pi-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker pi

# Install Docker Compose
sudo apt install docker-compose -y

# Logout and login for group changes
exit
ssh pi@<your-pi-ip>
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/msannikov03/alfa-hackathon.git
cd alfa-hackathon

# Configure environment
cp .env.example .env
nano .env
```

**Update .env for production:**
```env
# Change these
POSTGRES_PASSWORD=<strong_password>
JWT_SECRET=<generate_with_openssl_rand_hex_32>

# Add your keys
LLM7_API_KEY=your_token_here...
TELEGRAM_BOT_TOKEN=123456:ABC...

# Set your domain (configure in Part 2)
TELEGRAM_WEBAPP_URL=https://yourdomain.com/tg-app
NEXT_PUBLIC_API_URL=https://yourdomain.com
```

---

## Part 2: Cloudflare Tunnel

Cloudflare Tunnel exposes your Pi securely without opening ports.

### 1. Install Cloudflared

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb
```

### 2. Authenticate

```bash
cloudflared tunnel login
```

Browser opens → Login to Cloudflare → Authorize

### 3. Create Tunnel

```bash
cloudflared tunnel create alfa-assistant
```

**Save the Tunnel ID** from output: `Tunnel credentials written to /home/pi/.cloudflared/<TUNNEL_ID>.json`

### 4. Configure Tunnel

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

**Add this (replace YOUR_TUNNEL_ID and yourdomain.com):**
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/pi/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: yourdomain.com
    service: http://localhost:3000
  - service: http_status:404
```

### 5. Route DNS

```bash
cloudflared tunnel route dns alfa-assistant yourdomain.com
```

### 6. Start Tunnel as Service

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
sudo systemctl status cloudflared
```

### 7. Test Deployment

```bash
cd ~/alfa-hackathon
docker compose up -d
docker exec alfa_backend python seed_demo_data.py

# Check services
docker compose ps
curl http://localhost:8000/health

# Check public access
curl https://yourdomain.com
```

---

## Part 3: CI/CD Auto-Deploy

Auto-deploy on every push to main branch.

### 1. Generate SSH Key on Pi

```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Add to authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# Copy private key (you'll need this for GitHub)
cat ~/.ssh/github_actions
```

### 2. Add GitHub Secrets

Go to: `https://github.com/YOUR_USERNAME/alfa-hackathon/settings/secrets/actions`

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `PI_HOST` | Your Pi's IP address (e.g., `192.168.1.100`) |
| `PI_USER` | `pi` |
| `PI_SSH_KEY` | Entire content of `~/.ssh/github_actions` (private key) |

### 3. Verify Workflow File

The workflow file already exists at `.github/workflows/deploy.yml`. It will:
1. Connect to your Pi via SSH
2. Pull latest code
3. Rebuild Docker images
4. Restart services
5. Check health

### 4. Test Auto-Deploy

```bash
# On your local machine
cd alfa-hackathon
echo "# Test deploy" >> README.md
git add .
git commit -m "Test auto-deploy"
git push origin main

# Watch deployment at:
# https://github.com/YOUR_USERNAME/alfa-hackathon/actions
```

**Deployment takes ~2-3 minutes.**

### 5. Ensure Auto-Build Works

The workflow **automatically builds** on every push. To verify:

1. **Check GitHub Actions tab** - Should see workflow running
2. **Check Pi logs:**
   ```bash
   cd ~/alfa-hackathon
   docker compose logs -f
   ```
3. **Verify new code is deployed:**
   ```bash
   git log -1  # Should show latest commit
   ```

**If deployment fails:**
- Check GitHub Actions logs for errors
- Verify SSH key is correct
- Test manual SSH: `ssh -i ~/.ssh/github_actions pi@<pi-ip>`
- Check Pi has enough disk space: `df -h`

---

## Part 4: Post-Deployment

### 1. Update Telegram Bot

Talk to @BotFather:
```
/mybots
→ Select your bot
→ Bot Settings
→ Menu Button
→ Send: https://yourdomain.com/tg-app
```

### 2. Set Bot Commands

Talk to @BotFather:
```
/mybots
→ Select your bot
→ Edit Commands
```

Send:
```
start - Choose Demo or Live mode
briefing - Get today's briefing
stats - View statistics
approve - Check pending approvals
setup - Configure business profile
changemode - Switch modes
help - Show help
```

### 3. Verify Everything

**Dashboard:** https://yourdomain.com/login
- Login: `demo_admin` / `demo123`

**Telegram:**
- `/start` → Choose Demo Mode
- `/briefing` → See full briefing

---

## Maintenance

### View Logs

```bash
# On Pi
cd ~/alfa-hackathon

# Backend logs
docker compose logs -f backend

# All services
docker compose logs -f
```

### Manual Deploy

```bash
# On Pi
cd ~/alfa-hackathon
git pull origin main
docker compose down
docker compose build
docker compose up -d
```

### Restart Services

```bash
docker compose restart backend
docker compose restart frontend
```

### Check Cloudflare Tunnel

```bash
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -f
```

### Update Environment Variables

```bash
nano ~/alfa-hackathon/.env
docker compose restart
```

---

## Troubleshooting

**Auto-deploy not triggering:**
- Check GitHub Actions is enabled
- Verify secrets are correct (PI_HOST, PI_USER, PI_SSH_KEY)
- Check workflow file exists: `.github/workflows/deploy.yml`

**Build fails on Pi:**
- Check disk space: `df -h`
- Clean old images: `docker system prune -a`
- Check Docker is running: `docker ps`

**Cloudflare Tunnel down:**
```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

**Can't access https://yourdomain.com:**
- Check Cloudflare DNS is configured
- Verify tunnel is running: `sudo systemctl status cloudflared`
- Check local services: `curl http://localhost:3000`

**Database reset needed:**
```bash
docker compose down -v
docker compose up -d
docker exec alfa_backend python seed_demo_data.py
```

---

## Summary

**What you've done:**
1. ✅ Raspberry Pi running Docker services
2. ✅ Cloudflare Tunnel for public HTTPS access
3. ✅ GitHub Actions auto-deploy on push to main
4. ✅ Production environment configured

**Workflow:**
```
Code change → git push → GitHub Actions → SSH to Pi → Pull & Build → Restart → Live!
```

**Every push to `main` branch automatically deploys in ~2-3 minutes.**

No manual deployment needed! Just push and it's live 🚀
