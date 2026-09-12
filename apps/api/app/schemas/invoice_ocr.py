# apps/api/app/schemas/invoice_ocr.py

import re
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator


class InvoiceLineItem(BaseModel):
    description: str = Field(description="Description of goods or services supplied")
    hsn_sac_code: Optional[str] = Field(default=None, description="HSN or SAC classification code")
    quantity: Decimal = Field(default=Decimal("1.0"), description="Quantity supplied")
    unit_price: Decimal = Field(gt=Decimal("0.00"), description="Unit price per item")
    taxable_amount: Decimal = Field(gt=Decimal("0.00"), description="Total line taxable base value")
    gst_rate_percent: Decimal = Field(default=Decimal("18.0"), description="Applicable GST slab (e.g. 5, 12, 18, 28)")

    @field_validator("quantity", "unit_price", "taxable_amount", "gst_rate_percent", mode="before")
    def parse_decimals(cls, v):
        return Decimal(str(v))


class StructuredInvoiceOutput(BaseModel):
    """
    Guaranteed structured output schema for Indian B2B Invoices under GST and MSME Section 43B(h).
    """
    # Vendor Identity
    vendor_name: str = Field(
        description="Legal business name or trade name of the supplier entity"
    )
    vendor_pan: str = Field(
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
        description="10-character Permanent Account Number (PAN) of the supplier"
    )
    vendor_gstin: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",
        description="15-character Goods and Services Tax Identification Number"
    )
    is_udyam_registered: bool = Field(
        default=False,
        description="True if invoice explicitly prints an Udyam Registration Number"
    )
    udyam_registration_number: Optional[str] = Field(
        default=None,
        description="Udyam number if visible on invoice header/footer (e.g., UDYAM-MH-01-0012345)"
    )

    # Document Dates & Identifiers
    invoice_number: str = Field(
        description="Unique supplier tax invoice or bill reference number"
    )
    invoice_date: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Invoice issuance date in ISO format (YYYY-MM-DD)"
    )
    delivery_or_challan_date: Optional[str] = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Goods receipt or delivery challan date if stated on document"
    )

    # Financial & Tax Amounts
    taxable_amount: Decimal = Field(
        gt=Decimal("0.00"),
        description="Base taxable value excluding GST (subject to 43B(h) disallowance)"
    )
    cgst_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        description="Central GST amount charged"
    )
    sgst_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        description="State GST amount charged"
    )
    igst_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        description="Integrated GST amount charged (inter-state)"
    )
    total_amount: Decimal = Field(
        gt=Decimal("0.00"),
        description="Total invoice payable value inclusive of all taxes"
    )

    # Statutory Credit Terms
    detected_credit_terms_days: int = Field(
        default=15,
        ge=0,
        le=180,
        description="Credit terms in days. Defaults strictly to 15 if missing on document"
    )
    has_written_contract_indicators: bool = Field(
        default=False,
        description="True if invoice references a Purchase Order (PO), contract, or credit clause"
    )
    po_reference_number: Optional[str] = Field(
        default=None,
        description="Purchase Order reference number if visible"
    )

    # TDS Section
    tds_section_applicable: Literal["194C", "194J", "194Q", "194H", "NONE"] = Field(
        default="NONE",
        description="Detected Income Tax TDS Section based on line-item description"
    )

    # Line Item Breakdown
    line_items: List[InvoiceLineItem] = Field(
        default_factory=list,
        description="Extracted line items from the bill table"
    )

    @field_validator("vendor_pan", mode="before")
    def clean_pan(cls, v: str) -> str:
        return re.sub(r"[^A-Za-z0-9]", "", str(v)).upper()

    @field_validator("vendor_gstin", mode="before")
    def clean_gstin(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = re.sub(r"[^A-Za-z0-9]", "", str(v)).upper()
        return clean if clean else None

    @field_validator("taxable_amount", "cgst_amount", "sgst_amount", "igst_amount", "total_amount", mode="before")
    def parse_financial_amounts(cls, v):
        return Decimal(str(v))
