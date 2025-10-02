"""
SPL Shield Telegram Bot - Main Entry Point
Connects to backend API at localhost:8000
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import get_settings
from handlers import user, admin, payment, scanning
from middleware.auth import AuthMiddleware
from services.api_service import APIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot entry point"""
    
    # Load settings
    settings = get_settings()
    
    logger.info(f"🤖 Starting SPL Shield Bot...")
    logger.info(f"📡 Backend API: {settings.API_BASE_URL}")
    logger.info(f"👥 Admin IDs: {settings.admin_ids}")
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Initialize API service
    api_service = APIService(base_url=settings.API_BASE_URL)
    
    # Register middleware with api_service
    dp.message.middleware(AuthMiddleware(api_service))
    dp.callback_query.middleware(AuthMiddleware(api_service))
    
    # Include routers
    dp.include_router(user.router)
    dp.include_router(scanning.router)
    dp.include_router(payment.router)
    dp.include_router(admin.router)
    
    logger.info("✅ SPL Shield Bot is ready!")
    logger.info("🚀 Starting polling...")
    
    try:
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await api_service.close()


if __name__ == "__main__":
    asyncio.run(main())