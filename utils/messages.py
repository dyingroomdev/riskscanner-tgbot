# === utils/messages.py ===
"""All bot messages and text content"""

# Welcome & Start Messages
WELCOME_MESSAGE = """
🛡️ <b>Welcome to SPL Shield!</b>

I am your Solana risk co-pilot. Run instant token & wallet scans, get AI recommendations, and stay on top of on-chain threats.

<b>🎯 Service Tiers:</b>
💚 <b>Free</b> – 5 scans/day with essential checks  
⭐ <b>Premium</b> – Enhanced liquidity & holder analytics (10 TDL per scan)  
🚀 <b>MVP</b> – Full AI suite with MEV, rugpull & sentiment analysis (50 TDL per scan)

<b>⚡ Quick Start:</b>
1. /register and verify your email  
2. /login to link your account  
3. /scan any token or wallet address

Tap the buttons below or type /help for the full command list.
"""

HELP_MESSAGE = """
📚 <b>SPL Shield • Command Guide</b>

<b>👤 User Commands</b>
/start – Welcome message & menu  
/help – Display this guide  
/register – Create a new account  
/login – Sign in after email verification  
/logout – Disconnect the bot  
/dashboard – Account overview & credits  
/scan – Analyze a token or wallet  
/history – Show recent scans  
/balance – View TDL & credit balances  
/upgrade – Tier benefits & instructions

<b>💳 Payment Commands</b>
/buy_credits – View purchase instructions  
/pricing – Tier & credit pricing  
/verify_payment &lt;tx&gt; [tier] – Confirm a TDL purchase

<b>🛠️ Admin Commands (admin only)</b>
/admin – High level dashboard  
/stats – Credit & usage breakdown  
/users – Recent users snapshot  
/transactions – Payment activity summary

💡 Pro tips:
• Inline buttons mirror the most common actions  
• Risk scores are 0–1 (higher = riskier)  
• Premium/MVP scans consume credits or direct TDL

Need help? @splsupportbot
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
✅ <b>Registration Submitted!</b>

Welcome aboard, {username}!  
We just sent a verification email to <b>{email}</b>.

<b>Next Steps:</b>
1. Open the email and click the verification link  
2. Return here and use /login  
3. Start scanning with /scan

Email verification is required before logging in.
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
• Free credits remaining: {free_credits}
• Premium credits: {premium_credits}
• MVP credits: {mvp_credits}
• TDL balance: {tdl_balance}

Use /scan to analyze a new address or /dashboard for a full overview.
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

Premium/MVP tiers may take a few extra seconds while we gather AI insights.
"""

SCAN_RESULT_TEMPLATE = """
📊 <b>Scan Results</b>

<b>Address:</b> <code>{address}</code>
<b>Type & Tier:</b> {type}
<b>Risk Score:</b> {risk_score} / 1.0 {risk_emoji}
<b>Risk Level:</b> {risk_level}

<b>🔍 Analysis</b>
{analysis_summary}

<b>⚠️ Risk Factors</b>
{risk_factors}

<b>✅ Positive Signals</b>
{safe_indicators}

<b>🤖 AI Insight</b>
{ai_summary}

<b>📈 Recommendation</b>
{recommendation}
"""

# Dashboard Message
DASHBOARD_TEMPLATE = """
📊 <b>Your Dashboard</b>

<b>Account</b>
• Email: {email}
• Username: {username}
• Tier: {tier}
• Member since: {created_at}

<b>Credits</b>
• Free: {credits_free}
• Premium: {credits_premium}
• MVP: {credits_mvp}
• TDL balance: {tdl_balance}

<b>Usage</b>
• Scans remaining today: {scans_today}
• Daily limit: {daily_limit}
• Total scans (recent): {total_scans}

<b>Benefits</b>
{tier_benefits}

Need more power? Use /upgrade or /pricing.
"""

# Payment Messages
PRICING_MESSAGE = """
💎 <b>SPL Shield Pricing</b>

<b>Scan Tiers</b>
💚 Free – 5 scans/day, core risk checks (uses daily quota)  
⭐ Premium – Advanced liquidity & holder analytics (10 TDL per scan)  
🚀 MVP – Full AI insights, MEV & rugpull detection (50 TDL per scan)

<b>How to Pay</b>
1. Send TDL to the treasury wallet displayed in the web dashboard  
2. Use <code>/verify_payment &lt;tx_signature&gt; [premium|mvp]</code>  
3. Start scanning with the desired tier

Free credits reset daily. Premium/MVP credits never expire until used.
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
