import httpx
import os
from typing import Dict, Any, Optional

class UnifiedClient:
    """Client for interacting with Unified.to API for ERP integrations."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("UNIFIED_API_KEY", "")
        self.base_url = "https://api.unified.to"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if not self.api_key:
            print("Warning: UNIFIED_API_KEY is not set.")

    async def get_erp_metadata(self, connection_id: str) -> Dict[str, Any]:
        """Fetch unified schema metadata for a given ERP connection.
        Using a mock/accounting endpoint for demonstration purposes.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/accounting/connection/{connection_id}/metadata", 
                headers=self.headers
            )
            # In a real app we'd parse this robustly
            if response.status_code != 200:
                return {"error": f"Failed to fetch metadata, status: {response.status_code}"}
            return response.json()

    async def create_object(self, connection_id: str, category: str, object_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an object dynamically across any category in the connected ERP."""
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.base_url}/unified/{category}/{connection_id}/{object_type}",
                headers=self.headers,
                json=payload
            )
            return res.json()

    async def update_object(self, connection_id: str, category: str, object_type: str, object_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an object dynamically across any category in the connected ERP."""
        async with httpx.AsyncClient() as client:
            res = await client.patch(
                f"{self.base_url}/unified/{category}/{connection_id}/{object_type}/{object_id}",
                headers=self.headers,
                json=payload
            )
            return res.json()

    async def get_object(self, connection_id: str, category: str, object_type: str, object_id: str) -> Dict[str, Any]:
        """Fetches a specific object by its ID."""
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.base_url}/unified/{category}/{connection_id}/{object_type}/{object_id}",
                headers=self.headers
            )
            return res.json()

    async def passthrough_request(self, connection_id: str, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Raw fallback requests directly to the downstream API if universal endpoints do not handle it."""
        async with httpx.AsyncClient() as client:
            req_kwargs = {"headers": self.headers}
            if payload:
                req_kwargs["json"] = {"method": method, "path": path, "data": payload}
            else:
                req_kwargs["json"] = {"method": method, "path": path}

            res = await client.post(
                f"{self.base_url}/passthrough/{connection_id}",
                **req_kwargs
            )
            return res.json()
