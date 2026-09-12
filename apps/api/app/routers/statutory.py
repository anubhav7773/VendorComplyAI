# apps/api/app/routers/statutory.py

from fastapi import APIRouter, HTTPException, status
from app.schemas.statutory import InvoiceEvaluationRequest, InvoiceEvaluationResponse
from app.services.statutory_engine import MSMEStatutoryEngine

router = APIRouter(prefix="/statutory", tags=["Statutory Compliance Engine"])
engine = MSMEStatutoryEngine()


@router.post("/evaluate-invoice", response_model=InvoiceEvaluationResponse)
async def evaluate_single_invoice(req: InvoiceEvaluationRequest):
    """
    Evaluates an invoice for Section 43B(h) disallowance, Section 15 payment deadlines,
    and Section 16 monthly compounded penal interest.
    """
    try:
        result = engine.evaluate_invoice(req)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Statutory evaluation failed: {str(e)}"
        )
