# apps/api/tests/test_sync_router.py

import json
import hmac
import hashlib
import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_sync_push_success():
    tenant_id = "11111111-1111-1111-1111-111111111111"
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload = {
        "tenant_id": tenant_id,
        "timestamp": timestamp,
        "payload_data": {
            "ledgers": [{"name": "Vendor A", "pan": "ABCDE1234F", "gstin": "27ABCDE1234F1Z5", "credit_days": 30}],
            "vouchers": [],
            "payments": []
        }
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = hmac.new(settings.AGENT_HMAC_MASTER_KEY.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    response = client.post(
        "/api/v1/sync/push",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Tenant-ID": tenant_id,
            "X-Agent-Timestamp": timestamp,
            "X-Agent-Signature": sig
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["metrics"]["ledgers_synced"] == 1


def test_sync_push_invalid_signature():
    tenant_id = "11111111-1111-1111-1111-111111111111"
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload = {
        "tenant_id": tenant_id,
        "timestamp": timestamp,
        "payload_data": {
            "ledgers": [],
            "vouchers": [],
            "payments": []
        }
    }
    raw_body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/api/v1/sync/push",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Tenant-ID": tenant_id,
            "X-Agent-Timestamp": timestamp,
            "X-Agent-Signature": "invalid_signature"
        }
    )
    assert response.status_code == 403


def test_sync_push_replay_attack():
    tenant_id = "11111111-1111-1111-1111-111111111111"
    old_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=600)).isoformat()
    payload = {
        "tenant_id": tenant_id,
        "timestamp": old_time,
        "payload_data": {
            "ledgers": [],
            "vouchers": [],
            "payments": []
        }
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = hmac.new(settings.AGENT_HMAC_MASTER_KEY.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    response = client.post(
        "/api/v1/sync/push",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Tenant-ID": tenant_id,
            "X-Agent-Timestamp": old_time,
            "X-Agent-Signature": sig
        }
    )
    assert response.status_code == 401
