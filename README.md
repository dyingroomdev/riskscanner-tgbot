# === README.md ===
"""
# SPL Shield Telegram Bot

Telegram bot for SPL Shield - Solana Risk Scanner

## Features

- ✅ User registration & authentication
- ✅ Token & wallet scanning
- ✅ Multi-tier service (Free/Premium/MVP)
- ✅ TDL token payments
- ✅ Admin panel
- ✅ Scan history

## Prerequisites

1. **Get Bot Token:**
   - Message @BotFather on Telegram
   - Create new bot with `/newbot`
   - Copy the token

2. **Get Your Telegram ID:**
   - Message @userinfobot
   - Copy your user ID for admin access

## Installation

### Method 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone <your-repo>
cd splshield-telegram-bot

# 2. Create .env file
cat > .env << EOF
BOT_TOKEN=your_bot_token_here
API_BASE_URL=http://localhost:8000
ADMIN_USER_IDS=your_telegram_user_id
ENVIRONMENT=production
DEBUG=false
EOF

# 3. Build and run
docker-compose up -d

# 4. Check logs
docker-compose logs -f telegram-bot
```

### Method 2: Python Virtual Environment

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (same as above)

# 4. Run bot
python main.py
```

## Configuration

### Environment Variables (.env)

```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11  # From BotFather
API_BASE_URL=http://localhost:8000                    # Backend API URL
ADMIN_USER_IDS=123456789,987654321                   # Admin Telegram IDs
ENVIRONMENT=production
DEBUG=false
```

## Bot Commands

### User Commands
- `/start` - Welcome message
- `/help` - Command guide
- `/register` - Create account
- `/login` - Login
- `/logout` - Logout
- `/dashboard` - View dashboard
- `/scan` - Scan address
- `/history` - Scan history
- `/balance` - Check TDL balance
- `/upgrade` - Upgrade tier
- `/pricing` - View pricing

### Admin Commands (Admin Only)
- `/admin` - Admin panel
- `/stats` - System statistics
- `/users` - User management
- `/transactions` - Transaction history

## Usage Flow

1. **Registration:**
   ```
   /start → /register → Enter email → Create password → Choose username
   ```

2. **Login:**
   ```
   /login → Enter email → Enter password
   ```

3. **Scanning:**
   ```
   /scan → Enter address → Select tier → View results
   ```

4. **Check Balance:**
   ```
   /balance → View TDL balance and tier info
   ```

## File Structure

```
splshield-telegram-bot/
├── main.py              # Bot entry point
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── Dockerfile          # Docker config
├── docker-compose.yml  # Docker Compose
├── .env                # Environment variables
│
├── handlers/           # Command handlers
│   ├── user.py        # User commands
│   ├── scanning.py    # Scanning
│   ├── payment.py     # Payments
│   └── admin.py       # Admin panel
│
├── services/          # Services
│   └── api_service.py # Backend API
│
├── middleware/        # Middleware
│   └── auth.py       # Auth middleware
│
├── keyboards/        # Keyboards
│   └── user_kb.py   # User keyboards
│
└── utils/           # Utilities
    └── messages.py  # Bot messages
```

## Deployment on VPS

Since your backend runs on `localhost:8000`, deploy the bot on the **same VPS**:

```bash
# 1. SSH to your VPS
ssh user@your-vps-ip

# 2. Clone bot repository
git clone <your-repo>
cd splshield-telegram-bot

# 3. Create .env
nano .env
# Add: BOT_TOKEN, API_BASE_URL=http://localhost:8000, ADMIN_USER_IDS

# 4. Run with Docker
docker-compose up -d

# 5. Check status
docker-compose ps
docker-compose logs -f
```

## Troubleshooting

### Bot not responding
```bash
# Check logs
docker-compose logs telegram-bot

# Restart bot
docker-compose restart telegram-bot
```

### Can't connect to backend
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check network mode in docker-compose.yml
network_mode: host  # Must be set for localhost access
```

### Permission denied
```bash
# Make sure user has docker permissions
sudo usermod -aG docker $USER
```

## Support

- Documentation: [docs.splshield.com](https://docs.splshield.com)
- Support: @splshield_support
- Issues: GitHub Issues

## License

MIT
"""

print("✅ All files created!")
print("\n📁 File structure:")
print("- main.py")
print("- config.py")
print("- handlers/ (user.py, scanning.py, payment.py, admin.py)")
print("- services/ (api_service.py)")
print("- middleware/ (auth.py)")
print("- keyboards/ (user_kb.py)")
print("- utils/ (messages.py)")
print("- Dockerfile")
print("- docker-compose.yml")
print("- requirements.txt")
print("- README.md")