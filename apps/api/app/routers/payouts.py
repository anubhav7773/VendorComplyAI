# apps/api/app/routers/payouts.py

from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from decimal import Decimal
import datetime

from app.services.banking_exporter import (
    BankingBatchExporter,
    PayoutLineItem,
    BatchExportResult,
)

router = APIRouter(prefix="/payouts", tags=["Connected Banking Rails"])


class AuthorizeBatchRequest(BaseModel):
    bank_rail: Literal["ICICI_CIB", "HDFC_ENET"]
    batch_seq: int = Field(default=1, ge=1, le=999)
    client_debit_account: Optional[str] = Field(default="167105000250")
    client_code: Optional[str] = Field(default="HDFCCORP9988")
    items: List[PayoutLineItem]
    indemnification_confirmed: bool = Field(
        description="Mandatory statutory checkbox certifying beneficiary account verification."
    )
    authorized_by_role: Literal["PROMOTER_MD", "CFO", "ACCOUNTS_MANAGER", "AP_CLERK"] = Field(
        default="CFO"
    )


@router.post("/generate-batch", response_model=BatchExportResult)
async def generate_authorized_payment_batch(req: AuthorizeBatchRequest):
    """
    Maker-Checker Endpoint:
    Enforces corporate signatory roles, validates non-liability legal indemnification,
    and returns bank-compliant batch disbursement file metadata with SHA-256 fingerprint.
    """
    # 1. Role Authorization Check (Checker Role)
    if req.authorized_by_role not in ["PROMOTER_MD", "CFO", "ACCOUNTS_MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized. Only corporate signatories (Promoter/CFO/Accounts Manager) can authorize batch payouts.",
        )

    # 2. Mandatory Statutory Legal Indemnification Check
    if not req.indemnification_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Legal confirmation required. You must certify beneficiary verification before generating disbursement files.",
        )

    if not req.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch list cannot be empty.",
        )

    try:
        if req.bank_rail == "ICICI_CIB":
            result = BankingBatchExporter.generate_icici_cib_batch(
                batch_seq=req.batch_seq,
                client_debit_account=req.client_debit_account or "167105000250",
                items=req.items,
            )
        else:
            result = BankingBatchExporter.generate_hdfc_enet_batch(
                batch_seq=req.batch_seq,
                client_code=req.client_code or "HDFCCORP9988",
                items=req.items,
            )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch generation engine failed: {str(e)}",
        )


@router.post("/download-csv")
async def download_raw_batch_csv(req: AuthorizeBatchRequest):
    """
    Streams the generated bank batch CSV directly as an attachment with exact MIME headers.
    """
    if not req.indemnification_confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Indemnification confirmation required.")

    if req.bank_rail == "ICICI_CIB":
        result = BankingBatchExporter.generate_icici_cib_batch(
            batch_seq=req.batch_seq,
            client_debit_account=req.client_debit_account or "167105000250",
            items=req.items,
        )
    else:
        result = BankingBatchExporter.generate_hdfc_enet_batch(
            batch_seq=req.batch_seq,
            client_code=req.client_code or "HDFCCORP9988",
            items=req.items,
        )

    headers = {
        "Content-Disposition": f"attachment; filename={result.file_name}",
        "X-File-Checksum-SHA256": result.file_checksum_sha256,
    }
    return Response(content=result.file_content_csv, media_type="text/csv", headers=headers)
