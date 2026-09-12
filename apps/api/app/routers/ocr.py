# apps/api/app/routers/ocr.py

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.invoice_ocr import StructuredInvoiceOutput
from app.services.ocr_extractor import InvoiceOCRExtractor

router = APIRouter(prefix="/ocr", tags=["AI Invoice OCR"])
ocr_service = InvoiceOCRExtractor()


@router.post("/parse-invoice", response_model=StructuredInvoiceOutput)
async def upload_and_parse_invoice(file: UploadFile = File(...)):
    """
    Ingests invoice image or PDF file (max 10MB), executes OCR extraction,
    and returns mathematically verified statutory metadata.
    """
    allowed_extensions = (".pdf", ".png", ".jpg", ".jpeg", ".webp")
    lower_filename = file.filename.lower() if file.filename else ""

    if not any(lower_filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Permitted types: {', '.join(allowed_extensions)}",
        )

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum permitted limit of 10MB.",
        )

    try:
        extracted_invoice = ocr_service.extract_from_file_bytes(contents, file.filename)
        return extracted_invoice
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR extraction failed: {str(e)}",
        )
