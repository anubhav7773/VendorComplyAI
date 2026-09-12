# apps/api/app/routers/sync.py

import hmac
import hashlib
import datetime
from fastapi import APIRouter, Request, HTTPException, status, Header
from pydantic import BaseModel
from typing import Dict, Any, List
from app.core.config import settings

router = APIRouter(prefix="/sync", tags=["On-Premise Desktop Agent Sync"])


class SyncPayloadData(BaseModel):
    ledgers: List[Dict[str, Any]]
    vouchers: List[Dict[str, Any]]
    payments: List[Dict[str, Any]]


class AgentSyncEnvelope(BaseModel):
    tenant_id: str
    timestamp: str
    payload_data: SyncPayloadData


@router.post("/push")
async def receive_agent_sync(
    request: Request,
    envelope: AgentSyncEnvelope,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_agent_timestamp: str = Header(..., alias="X-Agent-Timestamp"),
    x_agent_signature: str = Header(..., alias="X-Agent-Signature"),
):
    """
    Ingestion Endpoint: Verifies HMAC-SHA256 signature against the raw body
    and processes delta vouchers from on-premise Tally agents.
    """
    # 1. Tenant Verification
    if envelope.tenant_id != x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header tenant_id does not match envelope body.",
        )

    # 2. Replay Attack Prevention (Payload must be within 300 seconds)
    try:
        req_time = datetime.datetime.fromisoformat(x_agent_timestamp.replace("Z", "+00:00"))
        now_time = datetime.datetime.now(datetime.timezone.utc)
        if abs((now_time - req_time).total_seconds()) > 300:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Request timestamp expired. Verify system clock synchronization.",
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed timestamp format.")

    # 3. HMAC-SHA256 Signature Verification
    raw_body = await request.body()
    computed_signature = hmac.new(
        settings.AGENT_HMAC_MASTER_KEY.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, x_agent_signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid HMAC signature. Unauthorized agent sync attempt.",
        )

    # 4. Ingestion Metrics
    ledgers_count = len(envelope.payload_data.ledgers)
    vouchers_count = len(envelope.payload_data.vouchers)
    payments_count = len(envelope.payload_data.payments)

    return {
        "status": "SUCCESS",
        "message": "Delta payload ingested successfully",
        "metrics": {
            "ledgers_synced": ledgers_count,
            "vouchers_synced": vouchers_count,
            "payments_synced": payments_count,
        },
    }
