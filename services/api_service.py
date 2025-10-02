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
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"API error: {response.status} - {error_text}")
                    return {"success": False, "error": error_text}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}
    
    # === User Authentication ===
    
    async def register(self, email: str, password: str, username: str, telegram_id: int) -> Dict:
        """Register new user"""
        return await self._make_request(
            "POST",
            "/api/auth/register",
            json={
                "email": email,
                "password": password,
                "username": username,
                "telegram_id": telegram_id
            }
        )
    
    async def login(self, email: str, password: str, telegram_id: int) -> Dict:
        """Login user"""
        return await self._make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": email,
                "password": password,
                "telegram_id": telegram_id
            }
        )
    
    async def logout(self, telegram_id: int) -> Dict:
        """Logout user"""
        return await self._make_request(
            "POST",
            "/api/auth/logout",
            json={"telegram_id": telegram_id}
        )
    
    async def get_user_profile(self, telegram_id: int) -> Optional[Dict]:
        """Get user profile"""
        result = await self._make_request(
            "GET",
            f"/api/users/profile/{telegram_id}"
        )
        return result.get('data') if result.get('success') else None
    
    # === Scanning ===
    
    async def scan_address(self, address: str, tier: str, telegram_id: int) -> Dict:
        """Scan Solana address"""
        return await self._make_request(
            "POST",
            "/api/scan",
            json={
                "address": address,
                "tier": tier,
                "telegram_id": telegram_id
            }
        )
    
    async def get_scan_history(self, telegram_id: int) -> list:
        """Get scan history"""
        result = await self._make_request(
            "GET",
            f"/api/scan/history/{telegram_id}"
        )
        return result.get('data', []) if result.get('success') else []
    
    # === Payments ===
    
    async def verify_payment(self, tx_signature: str, telegram_id: int) -> Dict:
        """Verify TDL payment"""
        return await self._make_request(
            "POST",
            "/api/payment/verify",
            json={
                "tx_signature": tx_signature,
                "telegram_id": telegram_id
            }
        )
    
    # === Admin ===
    
    async def get_admin_stats(self) -> Dict:
        """Get admin statistics"""
        result = await self._make_request("GET", "/api/admin/stats")
        return result.get('data', {})
    
    async def get_detailed_stats(self) -> Dict:
        """Get detailed statistics"""
        result = await self._make_request("GET", "/api/admin/stats/detailed")
        return result.get('data', {})
    
    async def get_all_users(self) -> list:
        """Get all users"""
        result = await self._make_request("GET", "/api/admin/users")
        return result.get('data', [])
    
    async def get_transactions(self) -> list:
        """Get transactions"""
        result = await self._make_request("GET", "/api/admin/transactions")
        return result.get('data', [])
