# === handlers/scanning.py ===
"""Scanning command handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.messages import (
    SCAN_PROMPT, SCAN_PROCESSING, SCAN_RESULT_TEMPLATE,
    ERROR_NOT_LOGGED_IN, ERROR_INVALID_ADDRESS, ERROR_SCAN_LIMIT
)
from keyboards.user_kb import get_scan_tier_keyboard, get_cancel_keyboard

router = Router()
logger = logging.getLogger(__name__)


class ScanStates(StatesGroup):
    waiting_for_address = State()
    selecting_tier = State()


@router.callback_query(F.data == "scan")
async def callback_scan(callback: CallbackQuery, state: FSMContext):
    """Kick off scanning from inline keyboard."""
    await cmd_scan(callback.message, state)
    await callback.answer()


@router.message(Command("scan"))
async def cmd_scan(message: Message, state: FSMContext):
    """Start scanning process"""
    await state.set_state(ScanStates.waiting_for_address)
    await message.answer(
        SCAN_PROMPT,
        reply_markup=get_cancel_keyboard()
    )


@router.message(ScanStates.waiting_for_address)
async def process_scan_address(message: Message, state: FSMContext):
    """Process the address to scan"""
    address = message.text.strip()
    
    # Basic Solana address validation (32-44 chars, base58)
    if len(address) < 32 or len(address) > 44:
        await message.answer(ERROR_INVALID_ADDRESS)
        return
    
    # Store address and show tier selection
    await state.update_data(address=address)
    await state.set_state(ScanStates.selecting_tier)
    
    logger.info(f"Address stored in state: {address}")
    
    await message.answer(
        "✅ Address validated!\n\n💎 Select scan tier:",
        reply_markup=get_scan_tier_keyboard()
    )


@router.callback_query(F.data.startswith("scan_tier:"))
async def process_scan_tier(callback: CallbackQuery, state: FSMContext, api_service):
    """Process tier selection and execute scan"""
    tier = callback.data.split(":")[1]
    data = await state.get_data()
    address = data.get('address')
    
    logger.info(f"Processing scan - Tier: {tier}, Address: {address}")
    
    if not address:
        await callback.message.answer("❌ Error: Address not found. Please try /scan again.")
        await state.clear()
        await callback.answer()
        return
    
    # Show processing message
    processing_msg = await callback.message.answer(
        SCAN_PROCESSING.format(address=address)
    )
    
    try:
        # Call API to scan
        logger.info(f"Calling scan_address with: address={address}, tier={tier}, telegram_id={callback.from_user.id}")
        
        result = await api_service.scan_address(
            address=address,
            tier=tier,
            telegram_id=callback.from_user.id,
        )
        
        logger.info(f"Scan result received: {result}")
        
        if result.get('success'):
            scan_data = result.get('data', {})
            risk_score = scan_data.get('risk_score', 0)
            risk_level = scan_data.get('risk_level', 'UNKNOWN')
            risk_factors = scan_data.get('risk_factors', [])
            safe_indicators = scan_data.get('safe_indicators', [])
            ai_summary = scan_data.get('ai_summary', 'No AI insights available')
            recommendation = scan_data.get('recommendation', 'Proceed with caution')
            
            risk_factors_text = '\n'.join([f"• {factor}" for factor in risk_factors]) or "None detected"
            safe_indicators_text = '\n'.join([f"• {indicator}" for indicator in safe_indicators]) or "None found"

            if risk_score < 0.25:
                risk_emoji = "🟢 LOW"
            elif risk_score < 0.5:
                risk_emoji = "🟡 MEDIUM"
            elif risk_score < 0.75:
                risk_emoji = "🟠 HIGH"
            else:
                risk_emoji = "🔴 CRITICAL"

            tier_used = scan_data.get("tier_used", tier).upper()
            header_note = scan_data.get("message") or "Analysis complete."

            await processing_msg.edit_text(
                SCAN_RESULT_TEMPLATE.format(
                    address=f"{address[:8]}...{address[-8:]}",
                    type=f"{scan_data.get('type', 'Unknown')} ({tier_used})",
                    risk_score=f"{risk_score:.2f}",
                    risk_level=risk_level,
                    risk_emoji=risk_emoji,
                    analysis_summary=header_note,
                    risk_factors=risk_factors_text,
                    safe_indicators=safe_indicators_text,
                    ai_summary=ai_summary,
                    recommendation=recommendation
                )
            )
        else:
            error_msg = result.get('error', 'Unknown error')
            await processing_msg.edit_text(
                f"❌ Scan failed: {error_msg}"
            )
    
    except Exception as e:
        logger.error(f"Scan error: {e}")
        await processing_msg.edit_text("❌ Scan failed. Please try again.")
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "history")
async def callback_history(callback: CallbackQuery, api_service):
    """Show scan history from inline button."""
    await cmd_history(callback.message, api_service)
    await callback.answer()


@router.message(Command("history"))
async def cmd_history(message: Message, api_service):
    """Show scan history"""
    try:
        history = await api_service.get_scan_history(telegram_id=message.from_user.id)
        
        if not history or len(history) == 0:
            await message.answer("📭 No scan history found.")
            return
        
        history_text = "📜 <b>Your Recent Scans</b>\n\n"
        
        for idx, scan in enumerate(history[:10], 1):  # Show last 10
            if isinstance(scan, dict):
                address = scan.get('address', 'N/A')
                tier = scan.get('tier', 'free').upper()
                risk_score_value = scan.get('risk_score')
                risk_score = f"{float(risk_score_value):.2f}" if isinstance(risk_score_value, (int, float)) else scan.get('risk_score', 'N/A')
                risk_level = scan.get('risk_level', 'UNKNOWN')
                created_at = scan.get('created_at') or scan.get('timestamp', 'N/A')
                history_text += (
                    f"{idx}. <code>{address[:8]}...{address[-8:]}</code>\n"
                    f"   Tier: {tier} | Risk: {risk_score} ({risk_level})\n"
                    f"   {created_at}\n\n"
                )
        
        await message.answer(history_text)
        
    except Exception as e:
        logger.error(f"History error: {e}")
        await message.answer("❌ Failed to load history.")
