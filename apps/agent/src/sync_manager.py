# apps/agent/src/sync_manager.py

import hmac
import hashlib
import json
import datetime
import requests
from decimal import Decimal
from typing import Dict, Any, List


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


class CloudSyncManager:
    """
    Packages delta vouchers, generates HMAC-SHA256 signatures,
    and handles TLS transmission to the backend cloud API.
    """

    def __init__(self, sync_url: str, tenant_id: str, secret_key: str):
        self.sync_url = sync_url
        self.tenant_id = tenant_id
        self.secret_key = secret_key

    def _generate_hmac(self, message_body: str) -> str:
        return hmac.new(
            self.secret_key.encode("utf-8"),
            message_body.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def push_delta_payload(
        self,
        ledgers: List[Dict[str, Any]],
        vouchers: List[Dict[str, Any]],
        payments: List[Dict[str, Any]]
    ) -> bool:
        if not ledgers and not vouchers and not payments:
            return True

        timestamp_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {
            "tenant_id": self.tenant_id,
            "timestamp": timestamp_iso,
            "payload_data": {
                "ledgers": ledgers,
                "vouchers": vouchers,
                "payments": payments
            }
        }

        body_serialized = json.dumps(payload, cls=DecimalEncoder)
        signature = self._generate_hmac(body_serialized)

        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": self.tenant_id,
            "X-Agent-Timestamp": timestamp_iso,
            "X-Agent-Signature": signature
        }

        try:
            res = requests.post(self.sync_url, data=body_serialized, headers=headers, timeout=30)
            if res.status_code == 200:
                return True
            print(f"[ERROR] Cloud Sync rejected with HTTP {res.status_code}: {res.text}")
            return False
        except Exception as e:
            print(f"[ERROR] Connection to cloud endpoint failed: {str(e)}")
            return False
