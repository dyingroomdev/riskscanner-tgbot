# 🤖 SPL Shield Telegram Bot - Complete Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Getting Started](#getting-started)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Command Reference](#command-reference)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### 1. Get Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name for your bot (e.g., "SPL Shield Bot")
   - Choose a username (must end in 'bot', e.g., "splshield_bot")
4. **Copy the token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. Save this token securely!

### 2. Get Your Telegram User ID (For Admin Access)

1. Open Telegram and search for **@userinfobot**
2. Send `/start` command
3. **Copy your User ID** (looks like: `123456789`)
4. This will be your admin ID

### 3. VPS Requirements

Your VPS should have:
- ✅ Backend API running on `localhost:8000`
- ✅ Docker & Docker Compose installed
- ✅ SSH access
- ✅ At least 1GB RAM

---

## 🚀 Getting Started

### Step 1: SSH into Your VPS

```bash
ssh your-user@your-vps-ip
```

### Step 2: Create Bot Directory

```bash
# Create directory for the bot
mkdir -p ~/splshield-telegram-bot
cd ~/splshield-telegram-bot
```

---

## 📦 Installation

### Option A: Manual File Creation (Recommended)

Create each file as shown below:

#### 1. Create `requirements.txt`
```bash
cat > requirements.txt << 'EOF'
aiogram==3.4.1
aiohttp==3.9.3
python-dotenv==1.0.0
pydantic==2.6.1
pydantic-settings==2.1.0
EOF
```

#### 2. Create `.env` file
```bash
cat > .env << 'EOF'
# Replace with your actual values
BOT_TOKEN=your_bot_token_from_botfather
API_BASE_URL=http://localhost:8000
ADMIN_USER_IDS=your_telegram_user_id
ENVIRONMENT=production
DEBUG=false
EOF
```

**⚠️ IMPORTANT:** Edit `.env` and replace:
- `your_bot_token_from_botfather` with your actual bot token
- `your_telegram_user_id` with your Telegram user ID

```bash
nano .env  # Edit the file
```

#### 3. Create `Dockerfile`
```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
EOF
```

#### 4. Create `docker-compose.yml`
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  telegram-bot:
    build: .
    container_name: splshield-telegram-bot
    restart: unless-stopped
    env_file:
      - .env
    network_mode: host
    volumes:
      - ./logs:/app/logs
EOF
```

#### 5. Create directory structure
```bash
mkdir -p handlers services middleware keyboards utils
touch handlers/__init__.py services/__init__.py middleware/__init__.py keyboards/__init__.py utils/__init__.py
```

#### 6. Copy all Python files

**Copy each file from the artifacts above:**
- `config.py`
- `main.py`
- `handlers/user.py`
- `handlers/scanning.py`
- `handlers/payment.py`
- `handlers/admin.py`
- `services/api_service.py`
- `middleware/auth.py`
- `keyboards/user_kb.py`
- `utils/messages.py`

Use `nano` or `vi` to create each file:
```bash
nano config.py  # Copy content from artifact
nano main.py    # Copy content from artifact
# ... and so on
```

### Option B: Using Git (If you have a repository)

```bash
git clone <your-repository-url>
cd splshield-telegram-bot
nano .env  # Create and configure
```

---

## ⚙️ Configuration

### Edit `.env` File

```bash
nano .env
```

**Required settings:**
```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
API_BASE_URL=http://localhost:8000
ADMIN_USER_IDS=123456789
ENVIRONMENT=production
DEBUG=false
```

**For multiple admins:**
```env
ADMIN_USER_IDS=123456789,987654321,555555555
```

---

## 🚀 Deployment

### Step 1: Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the bot
docker-compose up -d

# Check if running
docker-compose ps
```

### Step 2: Verify Bot is Running

```bash
# View logs
docker-compose logs -f telegram-bot

# You should see:
# ✅ SPL Shield Bot is ready!
# 🚀 Starting polling...
```

### Step 3: Test the Bot

1. Open Telegram
2. Search for your bot (e.g., `@splshield_bot`)
3. Send `/start` command
4. You should see the welcome message!

---

## 📚 Command Reference

### 👤 User Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show welcome message | `/start` |
| `/help` | Display help menu | `/help` |
| `/register` | Create new account | `/register` |
| `/login` | Login to account | `/login` |
| `/logout` | Logout from account | `/logout` |
| `/dashboard` | View account dashboard | `/dashboard` |
| `/scan` | Scan token/wallet address | `/scan` |
| `/history` | View scan history | `/history` |
| `/balance` | Check TDL balance | `/balance` |
| `/upgrade` | Upgrade service tier | `/upgrade` |
| `/pricing` | View pricing info | `/pricing` |
| `/buy_credits` | Purchase scan credits | `/buy_credits` |

### 🛠️ Admin Commands (Admin Only)

| Command | Description | Who Can Use |
|---------|-------------|-------------|
| `/admin` | Open admin panel | Admins only |
| `/stats` | View system statistics | Admins only |
| `/users` | Manage users | Admins only |
| `/transactions` | View transaction history | Admins only |

### 🔄 System Commands

| Command | Description |
|---------|-------------|
| `/cancel` | Cancel current operation |

---

## 📖 Usage Examples

### 1️⃣ User Registration Flow

```
User: /start
Bot: [Shows welcome message]

User: /register
Bot: Please enter your email address...

User: user@example.com
Bot: Email accepted! Now create a password...

User: MySecurePass123
Bot: Password set! Choose a username...

User: johndoe
Bot: ✅ Registration successful!
```

### 2️⃣ Login Flow

```
User: /login
Bot: Please enter your email address...

User: user@example.com
Bot: Email received! Enter your password...

User: MySecurePass123
Bot: ✅ Login successful! Welcome back, johndoe!
```

### 3️⃣ Scanning Flow

```
User: /scan
Bot: Please enter the Solana address...

User: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
Bot: ✅ Address validated! Select scan tier:
     [FREE] [PREMIUM] [MVP]

User: [Clicks FREE]
Bot: ⏳ Analyzing address... Please wait...
Bot: 📊 Scan Results
     Risk Score: 0.3/1.0 🟢 LOW
     [Analysis details...]
```

### 4️⃣ Dashboard

```
User: /dashboard
Bot: 📊 Your Dashboard
     
     Account Info:
     • Email: user@example.com
     • Tier: FREE
     • Scans Today: 2/5
     • Total Scans: 15
     • TDL Balance: 0.0
```

### 5️⃣ Admin Panel

```
Admin: /admin
Bot: 🛡️ SPL Shield Admin Panel
     
     System Stats:
     • Total Users: 150
     • Active Today: 45
     • Total Scans: 1,234
     • Scans Today: 89
```

---

## 🔧 Troubleshooting

### Problem: Bot not responding

**Solution:**
```bash
# Check if bot is running
docker-compose ps

# Check logs for errors
docker-compose logs telegram-bot

# Restart bot
docker-compose restart telegram-bot
```

### Problem: Can't connect to backend API

**Solution:**
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check network mode in docker-compose.yml
# Must have: network_mode: host

# 3. Check backend URL in .env
cat .env | grep API_BASE_URL
# Should be: API_BASE_URL=http://localhost:8000
```

### Problem: Bot responds but commands fail

**Solution:**
```bash
# Check API service logs
docker-compose logs telegram-bot | grep ERROR

# Verify .env configuration
cat .env

# Test API endpoint directly
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'
```

### Problem: Admin commands not working

**Solution:**
```bash
# 1. Verify your Telegram ID is in ADMIN_USER_IDS
cat .env | grep ADMIN_USER_IDS

# 2. Restart bot after changing .env
docker-compose down
docker-compose up -d

# 3. Check logs
docker-compose logs -f telegram-bot
```

### Problem: Docker build fails

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache

# Check disk space
df -h
```

---

## 📊 Monitoring

### View Real-time Logs
```bash
docker-compose logs -f telegram-bot
```

### Check Bot Status
```bash
docker-compose ps
```

### View Last 100 Lines
```bash
docker-compose logs --tail=100 telegram-bot
```

### Export Logs
```bash
docker-compose logs telegram-bot > bot_logs.txt
```

---

## 🔄 Maintenance

### Update Bot Code

```bash
# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup Configuration

```bash
# Backup .env file
cp .env .env.backup

# Backup entire directory
tar -czf splshield-bot-backup.tar.gz ~/splshield-telegram-bot/
```

### Stop Bot

```bash
# Stop bot
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🎉 Success Checklist

- [x] Bot token obtained from @BotFather
- [x] Admin user ID obtained from @userinfobot
- [x] All files created in correct structure
- [x] .env configured with correct values
- [x] Docker Compose running (`docker-compose ps` shows "Up")
- [x] Bot responds to `/start` in Telegram
- [x] Backend API accessible at localhost:8000
- [x] Registration and login working
- [x] Scanning functionality working
- [x] Admin commands accessible (for admin users)

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f telegram-bot`
2. Verify backend: `curl http://localhost:8000/health`
3. Test bot token: Send message to your bot on Telegram
4. Check file permissions: `ls -la`

---

## 🎯 Next Steps

After successful deployment:

1. **Customize Messages:** Edit `utils/messages.py`
2. **Add Features:** Create new handlers in `handlers/`
3. **Configure Payments:** Set up TDL wallet address
4. **Monitor Usage:** Use admin panel regularly
5. **Scale:** Consider adding rate limiting

---

**🛡️ Your SPL Shield Telegram Bot is now live!**

Users can now:
- Register and login
- Scan tokens and wallets
- View scan history
- Upgrade tiers
- Purchase credits with TDL

Admins can:
- Monitor system stats
- Manage users
- View transactions
- Check system health