# === handlers/admin.py ===
"""Admin command handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from config import get_settings

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    settings = get_settings()
    return user_id in settings.admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message, api_service):
    """Show admin panel (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ This command is for admins only.")
        return
    
    try:
        stats_overview = await api_service.get_admin_stats()
        users = stats_overview.get("users", {})
        revenue = stats_overview.get("revenue", {})
        usage = stats_overview.get("usage", {})

        await message.answer(
            f"🛡️ <b>SPL Shield Admin Panel</b>\n\n"
            f"<b>System Stats:</b>\n"
            f"• Total Users: {users.get('total', 0)}\n"
            f"• Verified Users: {users.get('verified', 0)} ({users.get('verification_rate', 0):.1f}%)\n"
            f"• New Users Today: {users.get('new_today', 0)}\n\n"
            f"<b>Revenue:</b>\n"
            f"• Total TDL: {revenue.get('total_tdl', 0)}\n"
            f"• Today: {revenue.get('today_tdl', 0)}\n"
            f"• Confirmed Transactions: {revenue.get('total_transactions', 0)}\n"
            f"• Pending Transactions: {revenue.get('pending_transactions', 0)}\n\n"
            f"<b>API Usage (24h):</b>\n"
            f"• Requests: {usage.get('requests_24h', 0)}\n"
            f"• Success Rate: {usage.get('success_rate', 0):.1f}%\n"
            f"• Unique Users: {usage.get('unique_users_24h', 0)}\n"
            f"• Avg req / hour: {usage.get('avg_requests_per_hour', 0):.1f}\n\n"
            f"Use /stats, /users, /transactions for details."
        )
    except Exception as e:
        logger.error(f"Admin panel error: {e}")
        await message.answer("❌ Failed to load admin panel.")


@router.message(Command("stats"))
async def cmd_stats(message: Message, api_service):
    """Show detailed statistics (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ This command is for admins only.")
        return
    
    try:
        stats = await api_service.get_detailed_stats()
        credits = stats.get("credits", {})
        tier_breakdown = credits.get("tier_breakdown", {})

        await message.answer(
            f"📊 <b>Detailed Statistics</b>\n\n"
            f"<b>Credit Distribution:</b>\n"
            f"• Total Distributed: {credits.get('total_distributed', 0)}\n"
            f"• Free Tier Users: {tier_breakdown.get('free', 0)}\n"
            f"• Premium Tier Users: {tier_breakdown.get('premium', 0)}\n"
            f"• MVP Tier Users: {tier_breakdown.get('mvp', 0)}\n\n"
            f"Use /users for user list, /transactions for payment activity."
        )
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await message.answer("❌ Failed to load statistics.")


@router.message(Command("users"))
async def cmd_users(message: Message, api_service):
    """Manage users (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ This command is for admins only.")
        return
    
    try:
        users = await api_service.get_all_users()
        
        user_list = "👥 <b>User Management</b>\n\n"
        for user in users[:20]:  # Show first 20
            username = user.get('username', 'Unknown')
            email = user.get('email', '—')
            tier = user.get('tier', 'free')
            total_spent = user.get('total_spent_tdl', 0)
            credits = user.get('credits', {})

            user_list += f"• {username} ({email})\n"
            user_list += f"  Tier: {tier.upper()} | Spent: {total_spent} TDL\n"
            if credits:
                user_list += (
                    f"  Credits - Free: {credits.get('free', 0)}, "
                    f"Premium: {credits.get('premium', 0)}, MVP: {credits.get('mvp', 0)}\n"
                )
            user_list += "\n"
        
        await message.answer(user_list)
    except Exception as e:
        logger.error(f"User management error: {e}")
        await message.answer("❌ Failed to load users.")


@router.message(Command("transactions"))
async def cmd_transactions(message: Message, api_service):
    """View transaction history (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ This command is for admins only.")
        return
    
    try:
        transactions = await api_service.get_transactions()
        if not transactions:
            await message.answer("ℹ️ Transaction metrics are not yet exposed by the API.")
            return

        tx_list = "💳 <b>Recent Transactions</b>\n\n"
        for tx in transactions[:15]:  # Show last 15
            tx_list += f"• {tx.get('user', 'Unknown')} - {tx.get('amount', 0)} TDL\n"
            tx_list += f"  Type: {tx.get('type', 'N/A')} | {tx.get('timestamp', 'N/A')}\n\n"
        
        await message.answer(tx_list)
    except Exception as e:
        logger.error(f"Transactions error: {e}")
        await message.answer("❌ Failed to load transactions.")
