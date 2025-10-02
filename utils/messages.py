# === utils/messages.py ===
"""All bot messages and text content"""

# Welcome & Start Messages
WELCOME_MESSAGE = """
🛡️ <b>Welcome to SPL Shield!</b>

Your trusted Solana Risk Analysis companion. I help you analyze tokens and wallets for potential risks before you invest.

<b>🔍 What I Can Do:</b>
• Scan Solana tokens for risk indicators
• Analyze wallet addresses for suspicious activity
• Provide AI-powered insights and recommendations
• Track your scan history

<b>🎯 Service Tiers:</b>
💚 <b>Free</b> - 5 scans/day, basic analysis
⭐ <b>Premium</b> - 50 scans/day, detailed insights
🚀 <b>MVP</b> - Unlimited scans, priority analysis

<b>⚡ Quick Start:</b>
1. Register with /register
2. Login with /login
3. Start scanning with /scan

Type /help to see all available commands!

Powered by TDL Token 💜
"""

HELP_MESSAGE = """
📚 <b>SPL Shield - Command Guide</b>

<b>👤 User Commands:</b>
/start - Show welcome message
/help - Display this help menu
/register - Create a new account
/login - Login to your account
/logout - Logout from your account
/dashboard - View your account dashboard
/scan - Scan a token or wallet address
/history - View your scan history
/balance - Check your TDL balance
/upgrade - Upgrade your service tier

<b>💳 Payment Commands:</b>
/buy_credits - Purchase scan credits with TDL
/pricing - View pricing information
/wallet - Show your payment wallet

<b>🛠️ Admin Commands:</b> (Admin Only)
/admin - Open admin panel
/stats - View system statistics
/users - Manage users
/transactions - View transaction history

<b>💡 Tips:</b>
• Use inline buttons for easier navigation
• Scan results include risk scores (0-1 scale)
• Higher scores = Higher risk
• Always verify contracts on blockchain explorers

Need help? Contact @splshield_support
"""

# Registration Messages
REGISTER_PROMPT = """
📝 <b>Account Registration</b>

Please enter your email address to register:
(We'll send you a verification code)

Example: user@example.com

Type /cancel to abort registration.
"""

REGISTER_SUCCESS = """
✅ <b>Registration Successful!</b>

Welcome to SPL Shield, {username}!

Your account has been created with:
• Email: {email}
• Tier: {tier}
• Daily Scans: {daily_scans}

You can now use /login to access your account.
"""

# Login Messages
LOGIN_PROMPT = """
🔐 <b>Account Login</b>

Please enter your email address:

Example: user@example.com

Type /cancel to abort login.
"""

LOGIN_SUCCESS = """
✅ <b>Login Successful!</b>

Welcome back, {username}!

• Tier: {tier}
• Scans Remaining: {scans_remaining}/{daily_limit}
• TDL Balance: {tdl_balance}

Ready to scan? Use /scan or /dashboard
"""

# Scan Messages
SCAN_PROMPT = """
🔍 <b>Address Scanner</b>

Please enter the Solana address you want to scan:

<b>Supported Types:</b>
• Token Contract Address
• Wallet Address

Example: 
<code>EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v</code>

Type /cancel to abort scanning.
"""

SCAN_PROCESSING = """
⏳ <b>Analyzing Address...</b>

Please wait while we analyze:
<code>{address}</code>

This may take 5-10 seconds...
"""

SCAN_RESULT_TEMPLATE = """
📊 <b>Scan Results</b>

<b>Address:</b> <code>{address}</code>
<b>Type:</b> {type}
<b>Risk Score:</b> {risk_score}/1.0 {risk_emoji}

<b>🔍 Analysis:</b>
{analysis_summary}

<b>⚠️ Risk Factors:</b>
{risk_factors}

<b>✅ Safe Indicators:</b>
{safe_indicators}

<b>🤖 AI Insight:</b>
{ai_summary}

<b>📈 Recommendation:</b> {recommendation}

Scanned with ❤️ by SPL Shield
"""

# Dashboard Message
DASHBOARD_TEMPLATE = """
📊 <b>Your Dashboard</b>

<b>Account Info:</b>
• Email: {email}
• Username: {username}
• Tier: {tier}
• Member Since: {created_at}

<b>📈 Usage Statistics:</b>
• Scans Today: {scans_today}/{daily_limit}
• Total Scans: {total_scans}
• TDL Balance: {tdl_balance}

<b>🎯 Service Tier Benefits:</b>
{tier_benefits}

Use /upgrade to unlock more features!
"""

# Payment Messages
PRICING_MESSAGE = """
💎 <b>SPL Shield Pricing</b>

<b>Service Tiers:</b>

💚 <b>FREE</b> - $0/month
• 5 scans per day
• Basic risk analysis
• Standard support

⭐ <b>PREMIUM</b> - 50 TDL/month
• 50 scans per day
• Advanced AI insights
• Priority support
• Detailed reports

🚀 <b>MVP</b> - 200 TDL/month
• Unlimited scans
• Real-time monitoring
• API access
• Dedicated support
• Custom alerts

<b>💰 Credit Packages:</b>
• 10 Credits = 10 TDL
• 50 Credits = 45 TDL (10% off)
• 100 Credits = 80 TDL (20% off)

Use /buy_credits to purchase!
"""

# Error Messages
ERROR_NOT_REGISTERED = "❌ You're not registered. Please use /register first."
ERROR_NOT_LOGGED_IN = "❌ Please login first with /login"
ERROR_INVALID_ADDRESS = "❌ Invalid Solana address. Please check and try again."
ERROR_SCAN_LIMIT = "❌ Daily scan limit reached. Upgrade your tier with /upgrade"
ERROR_INSUFFICIENT_BALANCE = "❌ Insufficient TDL balance. Use /buy_credits to add funds."
ERROR_GENERIC = "❌ Something went wrong. Please try again later."

# Success Messages
SUCCESS_LOGOUT = "✅ You've been logged out successfully."
SUCCESS_PAYMENT = "✅ Payment successful! Credits added to your account."