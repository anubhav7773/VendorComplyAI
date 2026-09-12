# apps/api/app/schemas/statutory.py

import datetime
from decimal import Decimal
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class PaymentItemSchema(BaseModel):
    payment_date: datetime.date
    amount: Decimal = Field(gt=Decimal("0.00"), description="Settled payment principal")

    @field_validator("amount", mode="before")
    def parse_amount(cls, v):
        return Decimal(str(v))


class InvoiceEvaluationRequest(BaseModel):
    invoice_id: str
    vendor_name: str
    udyam_category: Literal["MICRO", "SMALL", "MEDIUM", "UNREGISTERED"]
    is_trader: bool = Field(default=False, description="True if supplier is a Retail/Wholesale trader")
    nic_codes: List[str] = Field(default_factory=list, description="List of 2-digit or 5-digit NIC codes from Udyam")
    bill_date: datetime.date
    gross_amount: Decimal = Field(gt=Decimal("0.00"), description="Total invoice value including GST")
    agreed_credit_days: int = Field(default=0, ge=0, le=180, description="Agreed days. 0 if no written agreement")
    payments: List[PaymentItemSchema] = Field(default_factory=list)
    evaluation_date: Optional[datetime.date] = None
    corporate_tax_rate: Optional[Decimal] = None
    gst_claimed_as_itc: bool = Field(default=True, description="True if buyer claims GST Input Tax Credit")
    gst_rate_percent: Optional[Decimal] = None
    is_disputed: bool = Field(default=False, description="True if written objection lodged u/s 15 within 15 days")

    @field_validator("gross_amount", mode="before")
    def parse_gross_amount(cls, v):
        return Decimal(str(v))


class InvoiceEvaluationResponse(BaseModel):
    invoice_id: str
    vendor_name: str
    udyam_category: str
    is_trader: bool
    is_protected: bool
    bill_date: datetime.date
    statutory_credit_days: int
    statutory_due_date: datetime.date
    gross_amount: Decimal
    taxable_base_amount: Decimal
    total_paid: Decimal
    outstanding_principal: Decimal
    overdue_days: int
    is_overdue: bool
    effective_annual_penal_rate: Decimal
    accrued_penal_interest_sec16: Decimal
    tax_disallowance_base_sec43bh: Decimal
    potential_corporate_tax_exposure: Decimal
    total_statutory_exposure: Decimal
    status: Literal["UNPAID", "PARTIALLY_PAID", "PAID", "DISPUTED_HOLD"]
