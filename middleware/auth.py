# === middleware/auth.py ===
"""Authentication middleware"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class AuthMiddleware(BaseMiddleware):
    """Middleware to inject API service"""
    
    def __init__(self, api_service):
        self.api_service = api_service
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Inject API service into handler
        data['api_service'] = self.api_service
        return await handler(event, data)
