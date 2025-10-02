# === keyboards/user_kb.py ===
"""Telegram keyboard layouts"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_menu():
    """Main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Scan", callback_data="scan"),
            InlineKeyboardButton(text="📊 Dashboard", callback_data="dashboard")
        ],
        [
            InlineKeyboardButton(text="💰 Balance", callback_data="balance"),
            InlineKeyboardButton(text="📜 History", callback_data="history")
        ],
        [
            InlineKeyboardButton(text="💎 Upgrade", callback_data="upgrade"),
            InlineKeyboardButton(text="❓ Help", callback_data="show_help")
        ]
    ])


def get_scan_tier_keyboard():
    """Scan tier selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💚 FREE (Basic)", callback_data="scan_tier:free")],
        [InlineKeyboardButton(text="⭐ PREMIUM (Advanced)", callback_data="scan_tier:premium")],
        [InlineKeyboardButton(text="🚀 MVP (Unlimited)", callback_data="scan_tier:mvp")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])


def get_cancel_keyboard():
    """Simple cancel keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])


def get_payment_keyboard():
    """Payment options keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10 Credits - 10 TDL", callback_data="buy:10"),
        ],
        [
            InlineKeyboardButton(text="50 Credits - 45 TDL", callback_data="buy:50"),
        ],
        [
            InlineKeyboardButton(text="100 Credits - 80 TDL", callback_data="buy:100"),
        ],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])