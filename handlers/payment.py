# === handlers/payment.py ===
"""Payment and upgrade handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.messages import PRICING_MESSAGE, ERROR_NOT_LOGGED_IN
from keyboards.user_kb import get_main_menu

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

        credits = user_data.get('credits', {}) or {}
        await message.answer(
            f"💰 <b>Your Credits</b>\n\n"
            f"Tier: {user_data.get('tier', 'Free').upper()}\n"
            f"TDL Balance: {user_data.get('tdl_balance', 0.0)}\n\n"
            f"Free credits remaining: {credits.get('free', 0)}\n"
            f"Premium credits: {credits.get('premium', 0)}\n"
            f"MVP credits: {credits.get('mvp', 0)}\n\n"
            "Need more? Use /buy_credits or /pricing."
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
        "• Premium scan credit = 10 TDL\n"
        "• MVP scan credit = 50 TDL\n\n"
        "Send TDL to the treasury wallet and confirm with /verify_payment <tx_signature> <tier>."
    )


@router.message(Command("upgrade"))
async def cmd_upgrade(message: Message):
    """Show upgrade options"""
    await message.answer(
        "⬆️ <b>Upgrade Your Tier</b>\n\n"
        "⭐ <b>Premium</b>\n"
        "• Enhanced liquidity & holder analytics\n"
        "• 10 TDL per scan or premium credits\n\n"
        "🚀 <b>MVP</b>\n"
        "• Full AI analysis (MEV, rugpull, sentiment)\n"
        "• 50 TDL per scan or MVP credits\n\n"
        "Use /pricing for packages, /buy_credits to top up, then choose the tier when scanning."
    )


@router.message(Command("verify_payment"))
async def cmd_verify_payment(message: Message, api_service):
    """Verify a TDL payment transaction signature."""
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer(
            "Usage: <code>/verify_payment &lt;transaction_signature&gt; [tier]</code>\n"
            "Example: <code>/verify_payment 5Gx... premium</code>"
        )
        return

    tx_signature = parts[1]
    tier = parts[2].lower() if len(parts) > 2 else "premium"
    if tier not in {"premium", "mvp"}:
        await message.answer("Tier must be either <b>premium</b> or <b>mvp</b>.")
        return

    result = await api_service.verify_payment(tx_signature=tx_signature, tier=tier)
    if result.get("success"):
        await message.answer(f"✅ {result.get('message')}", reply_markup=get_main_menu())
    else:
        await message.answer(f"❌ Payment verification failed: {result.get('error')}")


@router.callback_query(F.data == "balance")
async def callback_balance(callback: CallbackQuery, api_service):
    await cmd_balance(callback.message, api_service)
    await callback.answer()


@router.callback_query(F.data == "upgrade")
async def callback_upgrade(callback: CallbackQuery):
    await cmd_upgrade(callback.message)
    await callback.answer()


@router.callback_query(F.data == "pricing")
async def callback_pricing(callback: CallbackQuery):
    await callback.message.answer(PRICING_MESSAGE)
    await callback.answer()
