# apps/api/tests/test_ocr_extractor.py

import io
from decimal import Decimal
import pytest
from PIL import Image
from pydantic import ValidationError
from app.schemas.invoice_ocr import StructuredInvoiceOutput, InvoiceLineItem
from app.services.document_preprocessor import DocumentPreprocessor


def test_schema_valid_indian_invoice():
    """
    Tests instantiation of a valid Indian B2B invoice matching statutory GST format.
    """
    payload = {
        "vendor_name": "Maheshwari Precision Castings Pvt Ltd",
        "vendor_pan": "AABCM1234K",
        "vendor_gstin": "27AABCM1234K1Z5",
        "is_udyam_registered": True,
        "udyam_registration_number": "UDYAM-MH-01-0012345",
        "invoice_number": "INV/2026/0491",
        "invoice_date": "2026-09-12",
        "taxable_amount": Decimal("250000.00"),
        "cgst_amount": Decimal("22500.00"),
        "sgst_amount": Decimal("22500.00"),
        "igst_amount": Decimal("0.00"),
        "total_amount": Decimal("295000.00"),
        "detected_credit_terms_days": 30,
        "has_written_contract_indicators": True,
        "po_reference_number": "PO-2026-8812",
        "tds_section_applicable": "194C",
        "line_items": [
            {
                "description": "CNC Machined Engine Blocks",
                "hsn_sac_code": "8409",
                "quantity": Decimal("50"),
                "unit_price": Decimal("5000.00"),
                "taxable_amount": Decimal("250000.00"),
                "gst_rate_percent": Decimal("18.0")
            }
        ]
    }

    invoice = StructuredInvoiceOutput(**payload)
    assert invoice.vendor_pan == "AABCM1234K"
    assert invoice.vendor_gstin == "27AABCM1234K1Z5"
    assert invoice.taxable_amount == Decimal("250000.00")
    assert invoice.total_amount == Decimal("295000.00")
    assert invoice.detected_credit_terms_days == 30
    assert invoice.tds_section_applicable == "194C"


def test_schema_pan_regex_enforcement():
    """
    Verifies that malformed PAN numbers fail Pydantic regex validation.
    """
    # 4th character is numeric instead of alphabetic
    invalid_payload = {
        "vendor_name": "Test Vendor",
        "vendor_pan": "AAB1M1234K",
        "invoice_number": "INV-001",
        "invoice_date": "2026-09-12",
        "taxable_amount": Decimal("10000.00"),
        "total_amount": Decimal("11800.00")
    }

    with pytest.raises(ValidationError):
        StructuredInvoiceOutput(**invalid_payload)


def test_unwritten_contract_defaults_to_15_days():
    """
    Verifies that if payment credit terms are omitted from the document,
    detected_credit_terms_days defaults strictly to 15 days under MSMED Section 15.
    """
    payload = {
        "vendor_name": "Quick Industrial Parts",
        "vendor_pan": "XYZPA9999M",
        "invoice_number": "QIP-901",
        "invoice_date": "2026-09-12",
        "taxable_amount": Decimal("40000.00"),
        "total_amount": Decimal("47200.00")
    }

    invoice = StructuredInvoiceOutput(**payload)
    assert invoice.detected_credit_terms_days == 15
    assert invoice.has_written_contract_indicators is False
    assert invoice.tds_section_applicable == "NONE"


def test_document_preprocessor_image_rescaling():
    """
    Verifies that images exceeding 1280px are safely scaled down while preserving RGB format.
    """
    # Create an in-memory 2000x1500 test image
    img = Image.new("RGB", (2000, 1500), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    processed_images = DocumentPreprocessor.process_raw_bytes(raw_bytes, "invoice.png")
    assert len(processed_images) == 1
    
    out_img = processed_images[0]
    width, height = out_img.size
    assert max(width, height) <= DocumentPreprocessor.MAX_DIMENSION
    assert out_img.mode == "RGB"


def test_ocr_router_unsupported_file_extension():
    """
    Verifies that files without supported extensions are rejected with 400 Bad Request.
    """
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    response = client.post(
        "/api/v1/ocr/parse-invoice",
        files={"file": ("invoice.exe", b"binarycontent", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_ocr_router_file_size_limit():
    """
    Verifies that files exceeding 10MB are rejected with 413 Payload Too Large.
    """
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    large_content = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/v1/ocr/parse-invoice",
        files={"file": ("large_invoice.pdf", large_content, "application/pdf")}
    )
    assert response.status_code == 413
    assert "File size exceeds maximum permitted limit" in response.json()["detail"]


def test_groq_vision_mock_extraction(monkeypatch):
    """
    Verifies that _extract_cloud properly calls Groq API with llama-3.2-11b-vision-preview
    and parses structured JSON invoice output.
    """
    from unittest.mock import MagicMock
    from app.services.ocr_extractor import InvoiceOCRExtractor

    mock_json_response = """{
        "vendor_name": "Groq Tested Components Ltd",
        "vendor_pan": "ABCDE1234F",
        "vendor_gstin": "27ABCDE1234F1Z5",
        "is_udyam_registered": true,
        "udyam_registration_number": "UDYAM-MH-01-0099887",
        "invoice_number": "INV-GROQ-001",
        "invoice_date": "2026-09-13",
        "taxable_amount": "150000.00",
        "cgst_amount": "13500.00",
        "sgst_amount": "13500.00",
        "igst_amount": "0.00",
        "total_amount": "177000.00",
        "detected_credit_terms_days": 30,
        "has_written_contract_indicators": true,
        "po_reference_number": "PO-9988",
        "tds_section_applicable": "194C",
        "line_items": []
    }"""

    extractor = InvoiceOCRExtractor()
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = mock_json_response
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    extractor.groq_client = mock_client

    test_img = Image.new("RGB", (300, 300), color=(255, 255, 255))
    result = extractor._extract_cloud(test_img)

    assert result.vendor_name == "Groq Tested Components Ltd"
    assert result.vendor_pan == "ABCDE1234F"
    assert result.total_amount == Decimal("177000.00")
    assert result.detected_credit_terms_days == 30
    assert mock_client.chat.completions.create.called
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "llama-3.2-11b-vision-preview"
    assert call_kwargs["response_format"] == {"type": "json_object"}


def test_groq_vision_missing_api_key_raises_error(monkeypatch):
    """
    Verifies that calling _extract_cloud without GROQ_API_KEY raises RuntimeError.
    """
    from app.services.ocr_extractor import InvoiceOCRExtractor
    from app.core.config import settings

    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    extractor = InvoiceOCRExtractor()
    extractor.groq_client = None
    extractor.use_local_gpu = False

    test_img = Image.new("RGB", (100, 100), color=(200, 200, 200))
    with pytest.raises(RuntimeError, match="GROQ_API_KEY is missing"):
        extractor._extract_cloud(test_img)


