"""
API Service - Handles all backend API communication
"""

import aiohttp
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class APIService:
    """Service for backend API communication"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        token: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make API request"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        headers = kwargs.pop('headers', {})
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"success": False, "error": "Unauthorized"}
                elif response.status == 429:
                    return {"success": False, "error": "Rate limit exceeded"}
                else:
                    text = await response.text()
                    logger.error(f"API error {response.status}: {text}")
                    return {"success": False, "error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Auth endpoints
    async def register(self, email: str, username: str, password: str) -> Dict[str, Any]:
        """Register new user"""
        return await self._request(
            'POST',
            '/api/auth/register',
            data={
                'email': email,
                'username': username,
                'password': password,
                'confirm_password': password
            }
        )
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        return await self._request(
            'POST',
            '/api/auth/login',
            data={
                'email': email,
                'password': password
            }
        )
    
    async def get_me(self, token: str) -> Dict[str, Any]:
        """Get current user info"""
        return await self._request('GET', '/api/auth/me', token=token)
    
    # Scanning endpoints
    async def scan_address(
        self, 
        address: str, 
        scan_type: str = "auto",
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Basic scan (free tier)"""
        return await self._request(
            'POST',
            '/api/scan',
            token=token,
            json={
                'address': address,
                'scan_type': scan_type
            }
        )
    
    async def scan_with_payment(
        self,
        address: str,
        tier: str,
        transaction_signature: Optional[str] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enhanced scan with payment"""
        data = {
            'address': address,
            'scan_type': 'auto',
            'tier': tier
        }
        if transaction_signature:
            data['transaction_signature'] = transaction_signature
        
        return await self._request(
            'POST',
            '/api/payment/scan-with-payment',
            token=token,
            json=data
        )
    
    async def get_scan_history(self, token: str) -> Dict[str, Any]:
        """Get scan history"""
        return await self._request(
            'GET',
            '/api/scan/history',
            token=token
        )
    
    # Payment endpoints
    async def get_pricing(self) -> Dict[str, Any]:
        """Get pricing info"""
        return await self._request('GET', '/api/payment/pricing')
    
    async def get_credits(self, token: str) -> Dict[str, Any]:
        """Get user credits"""
        return await self._request('GET', '/api/payment/credits', token=token)
    
    async def purchase_credits(
        self,
        tier: str,
        transaction_signature: str,
        token: str
    ) -> Dict[str, Any]:
        """Purchase credits"""
        return await self._request(
            'POST',
            '/api/payment/purchase',
            token=token,
            data={
                'tier': tier,
                'transaction_signature': transaction_signature
            }
        )
    
    # Admin endpoints
    async def get_dashboard_overview(self, token: str) -> Dict[str, Any]:
        """Get admin dashboard overview"""
        return await self._request(
            'GET',
            '/api/admin/dashboard/dashboard-overview',
            token=token
        )
    
    async def get_users(
        self, 
        token: str,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get users list"""
        params = {'page': page, 'limit': limit}
        if search:
            params['search'] = search
        
        return await self._request(
            'GET',
            '/api/admin/dashboard/users',
            token=token,
            params=params
        )
    
    async def get_transactions(
        self,
        token: str,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get transactions"""
        return await self._request(
            'GET',
            '/api/admin/dashboard/transactions',
            token=token,
            params={'page': page, 'limit': limit}
        )
    
    async def get_system_health(self, token: str) -> Dict[str, Any]:
        """Get system health"""
        return await self._request(
            'GET',
            '/api/admin/dashboard/system-health',
            token=token
        )
    
    async def get_analytics(
        self,
        token: str,
        period: str = "week"
    ) -> Dict[str, Any]:
        """Get analytics"""
        return await self._request(
            'GET',
            '/api/admin/dashboard/analytics',
            token=token,
            params={'period': period}
        )
    
    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return await self._request('GET', '/health')
    
    async def get_status(self) -> Dict[str, Any]:
        """Get API status"""
        return await self._request('GET', '/api/status')


class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        self.sessions: Dict[int, Dict[str, Any]] = {}
    
    def save_session(self, user_id: int, token: str, user_data: Dict[str, Any]):
        """Save user session"""
        self.sessions[user_id] = {
            'token': token,
            'user_data': user_data,
            'logged_in_at': datetime.now()
        }
    
    def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user session"""
        return self.sessions.get(user_id)
    
    def get_token(self, user_id: int) -> Optional[str]:
        """Get user token"""
        session = self.sessions.get(user_id)
        return session['token'] if session else None
    
    def logout(self, user_id: int):
        """Logout user"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def is_authenticated(self, user_id: int) -> bool:
        """Check if user is authenticated"""
        return user_id in self.sessions