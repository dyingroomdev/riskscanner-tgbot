# === handlers/user.py ===
"""User command handlers for SPL Shield Bot"""

import logging
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.messages import (
    WELCOME_MESSAGE, HELP_MESSAGE, REGISTER_PROMPT, 
    REGISTER_SUCCESS, LOGIN_PROMPT, LOGIN_SUCCESS,
    DASHBOARD_TEMPLATE, ERROR_NOT_REGISTERED, 
    ERROR_NOT_LOGGED_IN, SUCCESS_LOGOUT
)
from keyboards.user_kb import get_main_menu, get_cancel_keyboard

router = Router()
logger = logging.getLogger(__name__)


# FSM States
class RegisterStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()
    waiting_for_confirm_password = State()
    waiting_for_username = State()


class LoginStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()


# === /start Command ===
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command - Welcome message"""
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu()
    )


# === /help Command ===
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command - Show help menu"""
    await message.answer(HELP_MESSAGE)


# === /register Command ===
@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    """Start registration process"""
    await state.set_state(RegisterStates.waiting_for_email)
    await message.answer(
        REGISTER_PROMPT,
        reply_markup=get_cancel_keyboard()
    )


@router.message(RegisterStates.waiting_for_email)
async def process_register_email(message: Message, state: FSMContext):
    """Process email during registration"""
    email = message.text.strip()
    
    # Basic email validation
    if "@" not in email or "." not in email:
        await message.answer("❌ Invalid email format. Please try again:")
        return
    
    # Store email and ask for password
    await state.update_data(email=email)
    await state.set_state(RegisterStates.waiting_for_password)
    await message.answer(
        "✅ Email accepted!\n\n🔒 Now, create a strong password:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(RegisterStates.waiting_for_password)
async def process_register_password(message: Message, state: FSMContext):
    """Process password during registration"""
    password = message.text.strip()
    
    if len(password) < 6:
        await message.answer("❌ Password must be at least 6 characters. Try again:")
        return
    
    # Store password and ask for confirmation
    await state.update_data(password=password)
    await state.set_state(RegisterStates.waiting_for_confirm_password)
    await message.answer(
        "✅ Password set!\n\n🔒 Please confirm your password:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(RegisterStates.waiting_for_confirm_password)
async def process_register_confirm_password(message: Message, state: FSMContext):
    """Process password confirmation during registration"""
    confirm_password = message.text.strip()
    data = await state.get_data()
    password = data.get('password')
    
    if password != confirm_password:
        await message.answer("❌ Passwords don't match. Please enter your password again:")
        await state.set_state(RegisterStates.waiting_for_password)
        return
    
    # Store confirm_password and ask for username
    await state.update_data(confirm_password=confirm_password)
    await state.set_state(RegisterStates.waiting_for_username)
    await message.answer(
        "✅ Password confirmed!\n\n👤 Finally, choose a username:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(RegisterStates.waiting_for_username)
async def process_register_username(message: Message, state: FSMContext, api_service):
    """Complete registration process"""
    username = message.text.strip()
    
    if len(username) < 3:
        await message.answer("❌ Username must be at least 3 characters. Try again:")
        return
    
    # Get stored data
    data = await state.get_data()
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    # Call API to register with all required fields
    try:
        result = await api_service.register(
            email=email,
            password=password,
            confirm_password=confirm_password,
            username=username,
            telegram_id=message.from_user.id
        )
        
        if result.get('success'):
            await message.answer(
                REGISTER_SUCCESS.format(
                    username=username,
                    email=email,
                    tier=result.get('tier', 'Free'),
                    daily_scans=result.get('daily_scans', 5)
                ),
                reply_markup=get_main_menu()
            )
            await state.clear()
        else:
            error_msg = result.get('error', 'Unknown error')
            await message.answer(f"❌ Registration failed: {error_msg}")
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await message.answer("❌ Registration failed. Please try again later.")


# === /login Command ===
@router.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext):
    """Start login process"""
    await state.set_state(LoginStates.waiting_for_email)
    await message.answer(
        LOGIN_PROMPT,
        reply_markup=get_cancel_keyboard()
    )


@router.message(LoginStates.waiting_for_email)
async def process_login_email(message: Message, state: FSMContext):
    """Process email during login"""
    email = message.text.strip()
    
    await state.update_data(email=email)
    await state.set_state(LoginStates.waiting_for_password)
    await message.answer(
        "✅ Email received!\n\n🔒 Now enter your password:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(LoginStates.waiting_for_password)
async def process_login_password(message: Message, state: FSMContext, api_service):
    """Complete login process"""
    password = message.text.strip()
    data = await state.get_data()
    email = data.get('email')
    
    try:
        result = await api_service.login(
            email=email,
            password=password,
            telegram_id=message.from_user.id
        )
        
        if result.get('success'):
            user_data = result.get('user', {})
            await message.answer(
                LOGIN_SUCCESS.format(
                    username=user_data.get('username', 'User'),
                    tier=user_data.get('tier', 'Free'),
                    scans_remaining=user_data.get('scans_remaining', 0),
                    daily_limit=user_data.get('daily_limit', 5),
                    tdl_balance=user_data.get('tdl_balance', 0.0)
                ),
                reply_markup=get_main_menu()
            )
            await state.clear()
        else:
            await message.answer(f"❌ Login failed: {result.get('error', 'Invalid credentials')}")
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        await message.answer("❌ Login failed. Please try again.")


# === /logout Command ===
@router.message(Command("logout"))
async def cmd_logout(message: Message, api_service):
    """Handle logout"""
    try:
        result = await api_service.logout(telegram_id=message.from_user.id)
        await message.answer(SUCCESS_LOGOUT)
    except Exception as e:
        logger.error(f"Logout error: {e}")
        await message.answer("❌ Logout failed.")


# === /dashboard Command ===
@router.message(Command("dashboard"))
async def cmd_dashboard(message: Message, api_service):
    """Show user dashboard"""
    try:
        user_data = await api_service.get_user_profile(telegram_id=message.from_user.id)
        
        if not user_data:
            await message.answer(ERROR_NOT_LOGGED_IN)
            return
        
        tier_benefits = {
            'free': '• 5 scans/day\n• Basic analysis',
            'premium': '• 50 scans/day\n• Advanced AI insights',
            'mvp': '• Unlimited scans\n• Real-time monitoring'
        }
        
        await message.answer(
            DASHBOARD_TEMPLATE.format(
                email=user_data.get('email', 'N/A'),
                username=user_data.get('username', 'User'),
                tier=user_data.get('tier', 'Free').upper(),
                created_at=user_data.get('created_at', 'N/A'),
                scans_today=user_data.get('scans_today', 0),
                daily_limit=user_data.get('daily_limit', 5),
                total_scans=user_data.get('total_scans', 0),
                tdl_balance=user_data.get('tdl_balance', 0.0),
                tier_benefits=tier_benefits.get(user_data.get('tier', 'free').lower(), '')
            )
        )
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        await message.answer("❌ Failed to load dashboard.")


# === /cancel Command ===
@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    await message.answer(
        "❌ Operation cancelled.",
        reply_markup=get_main_menu()
    )


# === Callback Handlers ===
@router.callback_query(F.data == "show_help")
async def callback_help(callback: CallbackQuery):
    """Handle help button callback"""
    await callback.message.answer(HELP_MESSAGE)
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Handle main menu button callback"""
    await callback.message.answer(
        "🏠 Main Menu",
        reply_markup=get_main_menu()
    )
    await callback.answer()