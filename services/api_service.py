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
            
            async with session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response body: {response_text[:500]}")
                
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
        """Register new user - Backend expects FORM DATA not JSON"""
        logger.info(f"Registering user: {email}, username: {username}")
        
        session = await self._get_session()
        url = f"{self.base_url}/api/auth/register"
        
        # Backend expects application/x-www-form-urlencoded
        form_data = aiohttp.FormData()
        form_data.add_field('email', email)
        form_data.add_field('username', username)
        form_data.add_field('password', password)
        form_data.add_field('confirm_password', confirm_password)
        
        try:
            logger.info(f"Sending form data: email={email}, username={username}")
            async with session.post(url, data=form_data) as response:
                response_text = await response.text()
                logger.info(f"Registration response status: {response.status}")
                logger.info(f"Registration response: {response_text[:500]}")
                
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    return {
                        "success": True,
                        "tier": result.get("tier", "free"),
                        "daily_scans": result.get("daily_scans", 5),
                        "user": result
                    }
                else:
                    try:
                        error_data = await response.json()
                        return {"success": False, "error": error_data.get("detail", response_text)}
                    except:
                        return {"success": False, "error": response_text}
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {"success": False, "error": str(e)}
    
    async def login(self, email: str, password: str, telegram_id: int) -> Dict:
        """Login user - Backend expects FORM DATA"""
        logger.info(f"Login attempt for: {email}")
        
        session = await self._get_session()
        url = f"{self.base_url}/api/auth/login"
        
        # Backend expects application/x-www-form-urlencoded
        form_data = aiohttp.FormData()
        form_data.add_field('email', email)
        form_data.add_field('password', password)
        
        try:
            async with session.post(url, data=form_data) as response:
                response_text = await response.text()
                logger.info(f"Login response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "user": {
                            "username": result.get("username", "User"),
                            "email": email,
                            "tier": result.get("tier", "free"),
                            "scans_remaining": result.get("scans_remaining", 5),
                            "daily_limit": result.get("daily_limit", 5),
                            "tdl_balance": result.get("tdl_balance", 0.0)
                        },
                        "token": result.get("access_token")
                    }
                else:
                    return {"success": False, "error": "Invalid credentials"}
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {"success": False, "error": str(e)}
    
    async def logout(self, telegram_id: int) -> Dict:
        """Logout user"""
        return {"success": True, "message": "Logged out"}
    
    async def get_user_profile(self, telegram_id: int) -> Optional[Dict]:
        """Get user profile"""
        endpoints = [
            "/api/users/me",
            "/api/auth/me",
            f"/api/users/profile/{telegram_id}",
        ]
        
        for endpoint in endpoints:
            result = await self._make_request("GET", endpoint)
            if result.get('success') or result.get('email'):
                data = result.get('data', result)
                return {
                    "email": data.get("email", "N/A"),
                    "username": data.get("username", "User"),
                    "tier": data.get("tier", "free"),
                    "created_at": data.get("created_at", "N/A"),
                    "scans_today": data.get("scans_today", 0),
                    "daily_limit": data.get("daily_limit", 5),
                    "total_scans": data.get("total_scans", 0),
                    "tdl_balance": data.get("tdl_balance", 0.0)
                }
        
        return None
    
    # === Scanning ===
    
    async def scan_address(self, address: str, tier: str, telegram_id: int) -> Dict:
        """Scan Solana address"""
        result = await self._make_request(
            "POST",
            "/api/scan",
            json={
                "address": address,
                "scan_type": "auto"
            }
        )
        
        if result.get("success") or result.get("data"):
            data = result.get("data", result)
            return {
                "success": True,
                "data": {
                    "type": data.get("type", "token"),
                    "risk_score": data.get("risk_score", 0.5),
                    "analysis_summary": data.get("summary", data.get("analysis_summary", "Analysis complete")),
                    "risk_factors": data.get("risk_factors", []),
                    "safe_indicators": data.get("safe_indicators", []),
                    "ai_summary": data.get("ai_summary", "No AI insights available"),
                    "recommendation": data.get("recommendation", "Proceed with caution")
                }
            }
        return result
    
    async def get_scan_history(self, telegram_id: int) -> list:
        """Get scan history"""
        result = await self._make_request(
            "GET",
            f"/api/scan/history?limit=10"
        )
        return result.get('data', result.get('scans', []))
    
    # === Payments ===
    
    async def verify_payment(self, tx_signature: str, telegram_id: int) -> Dict:
        """Verify TDL payment"""
        session = await self._get_session()
        url = f"{self.base_url}/api/payment/purchase"
        
        form_data = aiohttp.FormData()
        form_data.add_field('tier', 'premium')
        form_data.add_field('transaction_signature', tx_signature)
        
        try:
            async with session.post(url, data=form_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": "Payment verification failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === Admin ===
    
    async def get_admin_stats(self) -> Dict:
        """Get admin statistics"""
        result = await self._make_request("GET", "/api/admin/dashboard")
        return result.get('data', result)
    
    async def get_detailed_stats(self) -> Dict:
        """Get detailed statistics"""
        result = await self._make_request("GET", "/api/admin/dashboard")
        return result.get('data', result)
    
    async def get_all_users(self) -> list:
        """Get all users"""
        result = await self._make_request("GET", "/api/users/")
        return result.get('data', result.get('users', []))
    
    async def get_transactions(self) -> list:
        """Get transactions"""
        result = await self._make_request("GET", "/api/payment/credits")
        return result.get('data', result.get('transactions', []))