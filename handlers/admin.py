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
        stats = await api_service.get_admin_stats()
        
        await message.answer(
            f"🛡️ <b>SPL Shield Admin Panel</b>\n\n"
            f"<b>System Stats:</b>\n"
            f"• Total Users: {stats.get('total_users', 0)}\n"
            f"• Active Today: {stats.get('active_today', 0)}\n"
            f"• Total Scans: {stats.get('total_scans', 0)}\n"
            f"• Scans Today: {stats.get('scans_today', 0)}\n\n"
            f"<b>Revenue:</b>\n"
            f"• Total TDL: {stats.get('total_revenue', 0)}\n"
            f"• Today: {stats.get('revenue_today', 0)}\n\n"
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
        
        await message.answer(
            f"📊 <b>Detailed Statistics</b>\n\n"
            f"<b>Users by Tier:</b>\n"
            f"• Free: {stats.get('free_users', 0)}\n"
            f"• Premium: {stats.get('premium_users', 0)}\n"
            f"• MVP: {stats.get('mvp_users', 0)}\n\n"
            f"<b>Scans:</b>\n"
            f"• Today: {stats.get('scans_today', 0)}\n"
            f"• This Week: {stats.get('scans_week', 0)}\n"
            f"• This Month: {stats.get('scans_month', 0)}\n\n"
            f"<b>System Health:</b>\n"
            f"• API Status: {stats.get('api_status', 'Unknown')}\n"
            f"• Uptime: {stats.get('uptime', 'N/A')}"
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
            user_list += f"• {user['username']} ({user['email']})\n"
            user_list += f"  Tier: {user['tier']} | Scans: {user['total_scans']}\n\n"
        
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
        
        tx_list = "💳 <b>Recent Transactions</b>\n\n"
        for tx in transactions[:15]:  # Show last 15
            tx_list += f"• {tx['user']} - {tx['amount']} TDL\n"
            tx_list += f"  Type: {tx['type']} | {tx['timestamp']}\n\n"
        
        await message.answer(tx_list)
    except Exception as e:
        logger.error(f"Transactions error: {e}")
        await message.answer("❌ Failed to load transactions.")