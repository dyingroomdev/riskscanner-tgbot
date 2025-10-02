# === handlers/payment.py ===
"""Payment and upgrade handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.messages import PRICING_MESSAGE, ERROR_NOT_LOGGED_IN

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("pricing"))
async def cmd_pricing(message: Message):
    """Show pricing information"""
    await message.answer(PRICING_MESSAGE)


@router.message(Command("balance"))
async def cmd_balance(message: Message, api_service):
    """Show TDL balance"""
    try:
        user_data = await api_service.get_user_profile(telegram_id=message.from_user.id)
        
        if not user_data:
            await message.answer(ERROR_NOT_LOGGED_IN)
            return
        
        await message.answer(
            f"💰 <b>Your TDL Balance</b>\n\n"
            f"Balance: {user_data.get('tdl_balance', 0.0)} TDL\n"
            f"Tier: {user_data.get('tier', 'Free').upper()}\n\n"
            f"Use /buy_credits to add more TDL!"
        )
    except Exception as e:
        logger.error(f"Balance check error: {e}")
        await message.answer("❌ Failed to check balance.")


@router.message(Command("buy_credits"))
async def cmd_buy_credits(message: Message):
    """Show credit purchase options"""
    await message.answer(
        "💳 <b>Purchase Credits</b>\n\n"
        "<b>Available Packages:</b>\n"
        "• 10 Credits = 10 TDL\n"
        "• 50 Credits = 45 TDL (10% off)\n"
        "• 100 Credits = 80 TDL (20% off)\n\n"
        "Send TDL to: <code>YOUR_WALLET_ADDRESS</code>\n\n"
        "After payment, use /verify_payment with transaction ID."
    )


@router.message(Command("upgrade"))
async def cmd_upgrade(message: Message):
    """Show upgrade options"""
    await message.answer(
        "⬆️ <b>Upgrade Your Tier</b>\n\n"
        "<b>Available Upgrades:</b>\n\n"
        "⭐ <b>PREMIUM</b> - 50 TDL/month\n"
        "• 50 scans per day\n"
        "• Advanced AI insights\n"
        "• Priority support\n\n"
        "🚀 <b>MVP</b> - 200 TDL/month\n"
        "• Unlimited scans\n"
        "• Real-time monitoring\n"
        "• API access\n"
        "• Dedicated support\n\n"
        "To upgrade, use /buy_credits first."
    )
