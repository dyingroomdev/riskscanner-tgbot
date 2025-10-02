# === services/api_service.py ===
"""API service for backend communication"""

import logging
import aiohttp
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class APIService:
    """Service to interact with SPL Shield backend API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making {method} request to {url}")
            if 'json' in kwargs:
                logger.info(f"Request payload: {kwargs['json']}")
            
            async with session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response body: {response_text[:200]}")
                
                if response.status == 200 or response.status == 201:
                    try:
                        return await response.json()
                    except:
                        return {"success": True, "data": response_text}
                else:
                    logger.error(f"API error: {response.status} - {response_text}")
                    try:
                        error_data = await response.json()
                        return {"success": False, "error": error_data.get("detail", response_text)}
                    except:
                        return {"success": False, "error": response_text}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}
    
    # === User Authentication ===
    
    async def register(self, email: str, password: str, confirm_password: str, username: str, telegram_id: int) -> Dict:
        """Register new user"""
        payload = {
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "username": username,
        }
        
        logger.info(f"Registering user: {email}, username: {username}")
        
        result = await self._make_request(
            "POST",
            "/api/auth/register",
            json=payload
        )
        
        # Transform response to expected format
        if result.get("success") or result.get("id") or result.get("email"):
            return {
                "success": True,
                "tier": result.get("tier", "free"),
                "daily_scans": result.get("daily_scans", 5),
                "user": result
            }
        return result
    
    async def login(self, email: str, password: str, telegram_id: int) -> Dict:
        """Login user"""
        return {"success": False, "error": "Not implemented yet"}
    
    async def logout(self, telegram_id: int) -> Dict:
        """Logout user"""
        return {"success": True, "message": "Logged out"}
    
    async def get_user_profile(self, telegram_id: int) -> Optional[Dict]:
        """Get user profile"""
        return None
    
    async def scan_address(self, address: str, tier: str, telegram_id: int) -> Dict:
        """Scan Solana address"""
        return {"success": False, "error": "Not implemented yet"}
    
    async def get_scan_history(self, telegram_id: int) -> list:
        """Get scan history"""
        return []
    
    async def verify_payment(self, tx_signature: str, telegram_id: int) -> Dict:
        """Verify TDL payment"""
        return {"success": False, "error": "Not implemented yet"}
    
    async def get_admin_stats(self) -> Dict:
        """Get admin statistics"""
        return {}
    
    async def get_detailed_stats(self) -> Dict:
        """Get detailed statistics"""
        return {}
    
    async def get_all_users(self) -> list:
        """Get all users"""
        return []
    
    async def get_transactions(self) -> list:
        """Get transactions"""
        return []
