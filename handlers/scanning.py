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


@router.message(Command("scan"))
async def cmd_scan(message: Message, state: FSMContext, api_service):
    """Start scanning process"""
    # Check if user is logged in
    user_data = await api_service.get_user_profile(telegram_id=message.from_user.id)
    
    if not user_data:
        await message.answer(ERROR_NOT_LOGGED_IN)
        return
    
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
    
    # Show processing message
    processing_msg = await callback.message.answer(
        SCAN_PROCESSING.format(address=address)
    )
    
    try:
        # Call API to scan
        result = await api_service.scan_address(
            address=address,
            tier=tier,
            telegram_id=callback.from_user.id
        )
        
        if result.get('success'):
            scan_data = result.get('data', {})
            
            # Format risk factors
            risk_factors = scan_data.get('risk_factors', [])
            risk_factors_text = '\n'.join([f"• {factor}" for factor in risk_factors]) or "None detected"
            
            # Format safe indicators
            safe_indicators = scan_data.get('safe_indicators', [])
            safe_indicators_text = '\n'.join([f"• {indicator}" for indicator in safe_indicators]) or "None found"
            
            # Risk emoji
            risk_score = scan_data.get('risk_score', 0)
            if risk_score < 0.3:
                risk_emoji = "🟢 LOW"
            elif risk_score < 0.7:
                risk_emoji = "🟡 MEDIUM"
            else:
                risk_emoji = "🔴 HIGH"
            
            # Send result
            await processing_msg.edit_text(
                SCAN_RESULT_TEMPLATE.format(
                    address=address[:8] + "..." + address[-8:],
                    type=scan_data.get('type', 'Unknown'),
                    risk_score=risk_score,
                    risk_emoji=risk_emoji,
                    analysis_summary=scan_data.get('analysis_summary', 'No summary available'),
                    risk_factors=risk_factors_text,
                    safe_indicators=safe_indicators_text,
                    ai_summary=scan_data.get('ai_summary', 'No AI insights available'),
                    recommendation=scan_data.get('recommendation', 'Proceed with caution')
                )
            )
        else:
            await processing_msg.edit_text(
                f"❌ Scan failed: {result.get('error', 'Unknown error')}"
            )
    
    except Exception as e:
        logger.error(f"Scan error: {e}")
        await processing_msg.edit_text("❌ Scan failed. Please try again.")
    
    await state.clear()
    await callback.answer()


@router.message(Command("history"))
async def cmd_history(message: Message, api_service):
    """Show scan history"""
    try:
        history = await api_service.get_scan_history(telegram_id=message.from_user.id)
        
        if not history:
            await message.answer("📭 No scan history found.")
            return
        
        history_text = "📜 <b>Your Scan History</b>\n\n"
        
        for idx, scan in enumerate(history[:10], 1):  # Show last 10
            history_text += f"{idx}. <code>{scan['address'][:8]}...{scan['address'][-8:]}</code>\n"
            history_text += f"   Risk: {scan['risk_score']:.2f} | {scan['timestamp']}\n\n"
        
        await message.answer(history_text)
        
    except Exception as e:
        logger.error(f"History error: {e}")
        await message.answer("❌ Failed to load history.")