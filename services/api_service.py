# === services/api_service.py ===
"""Async client for interacting with the SPL Shield backend API."""

import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class APIService:
    """Wrapper around aiohttp to communicate with the backend."""

    def __init__(self, base_url: str, host_header: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.host_header = host_header

    # ------------------------------------------------------------------
    # Session / request helpers
    # ------------------------------------------------------------------
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    def _with_auth(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        merged = dict(headers or {})
        if self.access_token and "Authorization" not in merged:
            merged["Authorization"] = f"Bearer {self.access_token}"
        if self.host_header:
            merged.setdefault("Host", self.host_header)
        return merged

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        expected_status: Optional[List[int]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        expected = set(expected_status or [200, 201])

        headers = kwargs.pop("headers", None)
        kwargs["headers"] = self._with_auth(headers)

        try:
            logger.debug("%s %s", method.upper(), url)
            async with session.request(method, url, **kwargs) as response:
                text = await response.text()
                logger.debug("Response %s: %s", response.status, text[:600])

                data: Any = None
                if text:
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        data = text

                if response.status in expected:
                    return {"ok": True, "status": response.status, "data": data}

                error_message = ""
                if isinstance(data, dict):
                    error_message = (
                        data.get("detail")
                        or data.get("error")
                        or data.get("message")
                        or text
                        or f"HTTP {response.status}"
                    )
                else:
                    error_message = data or f"HTTP {response.status}"

                logger.error("API error (%s %s): %s", method.upper(), url, error_message)
                return {
                    "ok": False,
                    "status": response.status,
                    "data": data,
                    "error": error_message,
                }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Request failed: %s %s", method.upper(), url)
            return {"ok": False, "status": 0, "data": None, "error": str(exc)}

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    async def register(
        self,
        *,
        email: str,
        password: str,
        confirm_password: str,
        username: str,
        telegram_id: int,  # noqa: ARG002 - kept for future auditing needs
    ) -> Dict[str, Any]:
        form = aiohttp.FormData()
        form.add_field("email", email)
        form.add_field("username", username)
        form.add_field("password", password)
        form.add_field("confirm_password", confirm_password)

        result = await self._request("POST", "/api/auth/register", data=form)
        if result["ok"]:
            payload = result["data"] or {}
            return {
                "success": True,
                "message": payload.get(
                    "message",
                    "Registration successful. Please verify your email before logging in.",
                ),
                "user_id": payload.get("user_id"),
            }

        return {"success": False, "error": result.get("error", "Registration failed")}

    async def login(
        self,
        *,
        email: str,
        password: str,
        telegram_id: int,  # noqa: ARG002 - future use
    ) -> Dict[str, Any]:
        form = aiohttp.FormData()
        form.add_field("email", email)
        form.add_field("password", password)

        result = await self._request("POST", "/api/auth/login", data=form)
        if not result["ok"]:
            return {"success": False, "error": result.get("error", "Login failed")}

        payload = result["data"] or {}
        token = payload.get("access_token")
        if token:
            self.access_token = token

        overview = await self.fetch_account_overview()

        user_info = overview.get("profile", {}).copy()
        user_info.setdefault("email", email)
        user_info["credits"] = overview.get("credits", {})

        return {
            "success": True,
            "token": token,
            "user": user_info,
            "message": payload.get("message", "Login successful"),
        }

    async def logout(self, telegram_id: int) -> Dict[str, Any]:  # noqa: ARG002
        self.access_token = None
        return {"success": True, "message": "Logged out"}

    # ------------------------------------------------------------------
    # Account helpers
    # ------------------------------------------------------------------
    async def fetch_account_overview(self) -> Dict[str, Any]:
        """Fetch profile + credit summary for the authenticated user."""
        profile_resp = await self._request("GET", "/api/users/me")
        credits_resp = await self._request("GET", "/api/payment/credits")

        profile_payload = {}
        if profile_resp["ok"]:
            data = profile_resp["data"] or {}
            profile_payload = data.get("user", data)

        credits_payload = {}
        if credits_resp["ok"]:
            data = credits_resp["data"] or {}
            credits_payload = data.get("credits", data)

        return {"profile": profile_payload, "credits": credits_payload}

    async def get_user_profile(self, telegram_id: int) -> Optional[Dict[str, Any]]:  # noqa: ARG002
        overview = await self.fetch_account_overview()
        profile = overview.get("profile")
        if not profile:
            return None

        credits = overview.get("credits", {}) or {}
        tier = profile.get("subscription_tier")
        if not tier:
            if credits.get("mvp_credits", 0) > 0:
                tier = "mvp"
            elif credits.get("premium_credits", 0) > 0:
                tier = "premium"
            else:
                tier = "free"

        scans_remaining = credits.get("free_credits")
        if scans_remaining is None and tier == "free":
            scans_remaining = 0

        return {
            "email": profile.get("email", "Unknown"),
            "username": profile.get("username", "User"),
            "tier": tier,
            "created_at": profile.get("created_at"),
            "last_login": profile.get("last_login"),
            "tdl_balance": profile.get("tdl_balance", 0.0),
            "credits": {
                "free": credits.get("free_credits"),
                "premium": credits.get("premium_credits"),
                "mvp": credits.get("mvp_credits"),
            },
            "scans_remaining": scans_remaining,
        }

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------
    def _normalise_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the relevant scan data from the API response."""
        analysis = payload.get("analysis") or {}
        risk_score = analysis.get("risk_score", payload.get("risk_score", 0))
        risk_level = analysis.get("risk_level", payload.get("risk_level", "UNKNOWN"))
        strengths = analysis.get("strengths") or payload.get("strengths") or []
        risk_factors_raw = analysis.get("risk_factors") or payload.get("risk_factors") or []
        recommendations = analysis.get("recommendations") or payload.get("recommendations") or []

        risk_factors: List[str] = []
        for item in risk_factors_raw:
            if isinstance(item, dict):
                risk_factors.append(
                    item.get("description")
                    or item.get("name")
                    or f"{item}"
                )
            else:
                risk_factors.append(str(item))

        return {
            "type": payload.get("scan_type", payload.get("type", "token")).upper(),
            "risk_score": float(risk_score or 0),
            "risk_level": str(risk_level or "UNKNOWN").upper(),
            "risk_factors": risk_factors or ["No significant risks detected."],
            "safe_indicators": strengths or ["Limited safe indicators available."],
            "ai_summary": payload.get("ai_summary") or analysis.get("ai_summary") or "No AI insight provided.",
            "recommendation": (recommendations[0] if recommendations else "Proceed with caution."),
        }

    def _select_primary_payload(self, data: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(data, dict):
            return None

        if "analysis" in data or "risk_score" in data:
            return data

        if "token" in data or "wallet" in data:
            token = data.get("token")
            wallet = data.get("wallet")
            return token or wallet

        return None

    async def scan_address(self, *, address: str, tier: str, telegram_id: int) -> Dict[str, Any]:  # noqa: ARG002
        payload = {
            "address": address,
            "scan_type": "auto",
            "tier": tier,
        }

        result = await self._request("POST", "/api/scan", json=payload)
        if not result["ok"]:
            error_text = result.get("error") or "Scan failed"
            if result["status"] == 402:
                error_text = "Insufficient credits. Purchase TDL or downgrade tier."
            if result["status"] == 429:
                error_text = "Daily scan limit reached. Upgrade tier for more scans."
            return {"success": False, "error": error_text}

        envelope = result.get("data") or {}
        scan_data = envelope.get("data", envelope)
        primary = self._select_primary_payload(scan_data)

        if not isinstance(primary, dict):
            return {"success": False, "error": "Unexpected scan response format."}

        normalised = self._normalise_analysis(primary)
        normalised["scan_id"] = envelope.get("scan_id")
        normalised["tier_used"] = envelope.get("tier", tier)
        normalised["message"] = envelope.get("message")

        return {"success": True, "data": normalised}

    async def get_scan_history(self, *, telegram_id: int, limit: int = 10) -> List[Dict[str, Any]]:  # noqa: ARG002
        result = await self._request(
            "GET",
            f"/api/scan/history?limit={limit}",
        )

        if not result["ok"]:
            return []

        data = result.get("data") or {}
        records = data.get("results", data.get("data", []))
        if isinstance(records, list):
            return records
        return []

    # ------------------------------------------------------------------
    # Payments / credits
    # ------------------------------------------------------------------
    async def verify_payment(self, *, tx_signature: str, tier: str) -> Dict[str, Any]:
        form = aiohttp.FormData()
        form.add_field("tier", tier)
        form.add_field("transaction_signature", tx_signature)

        result = await self._request("POST", "/api/payment/purchase", data=form)
        if result["ok"]:
            payload = result.get("data") or {}
            return {
                "success": True,
                "message": payload.get("message", "Payment processed successfully."),
            }

        return {
            "success": False,
            "error": result.get("error", "Payment verification failed."),
        }

    # ------------------------------------------------------------------
    # Admin utilities
    # ------------------------------------------------------------------
    async def get_admin_stats(self) -> Dict[str, Any]:
        result = await self._request("GET", "/api/admin/dashboard/dashboard-overview")
        if not result["ok"]:
            return {}
        payload = result.get("data") or {}
        return payload.get("overview", payload)

    async def get_detailed_stats(self) -> Dict[str, Any]:
        return await self.get_admin_stats()

    async def get_all_users(self) -> List[Dict[str, Any]]:
        result = await self._request("GET", "/api/admin/dashboard/users")
        if not result["ok"]:
            return []
        data = result.get("data") or {}
        return data.get("users", data.get("results", [])) or []

    async def get_transactions(self) -> List[Dict[str, Any]]:
        result = await self._request("GET", "/api/payment/credits")
        if result["ok"]:
            data = result.get("data") or {}
            txs = data.get("transactions")
            if isinstance(txs, list):
                return txs
        return []
