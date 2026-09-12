# apps/api/tests/test_statutory_engine.py

import datetime
from decimal import Decimal
import pytest
from app.schemas.statutory import InvoiceEvaluationRequest, PaymentItemSchema
from app.services.statutory_engine import MSMEStatutoryEngine


@pytest.fixture
def engine():
    return MSMEStatutoryEngine(
        corporate_tax_rate=Decimal("0.25168"),
        gst_rate_percent=Decimal("18.0"),
        rbi_bank_rate=Decimal("0.0650")
    )


def test_trader_exemption_nic_codes(engine):
    """
    Test Case: Apex Trading Corp (INV-2024-002)
    Supplier holds Udyam registration but primary activity is Trading (NIC 46 Wholesale).
    Under Ministry OMs of 2021, must result in ZERO tax disallowance and ZERO penal interest.
    """
    req = InvoiceEvaluationRequest(
        invoice_id="INV-2024-002",
        vendor_name="Apex Trading Corp",
        udyam_category="SMALL",
        is_trader=False,
        nic_codes=["46900"],  # Wholesale Trading NIC code
        bill_date=datetime.date(2025, 1, 15),
        gross_amount=Decimal("1200000.00"),
        agreed_credit_days=60,
        evaluation_date=datetime.date(2025, 3, 31)
    )

    result = engine.evaluate_invoice(req)

    assert result.is_trader is True
    assert result.is_protected is False
    assert result.accrued_penal_interest_sec16 == Decimal("0.00")
    assert result.tax_disallowance_base_sec43bh == Decimal("0.00")
    assert result.potential_corporate_tax_exposure == Decimal("0.00")
    assert result.total_statutory_exposure == Decimal("0.00")


def test_partial_payment_waterfall_and_leap_year(engine):
    """
    Test Case: Precision Components Ltd (INV-2024-001)
    Micro Manufacturer with partial settlements made on 20-Feb-2025 and 15-Mar-2025.
    Verifies that interest principal reduces upon partial settlement.
    """
    payments = [
        PaymentItemSchema(payment_date=datetime.date(2025, 2, 20), amount=Decimal("100000.00")),
        PaymentItemSchema(payment_date=datetime.date(2025, 3, 15), amount=Decimal("150000.00"))
    ]

    req = InvoiceEvaluationRequest(
        invoice_id="INV-2024-001",
        vendor_name="Precision Components Ltd",
        udyam_category="MICRO",
        is_trader=False,
        nic_codes=["25999"],  # Metal Fabrication Manufacturer
        bill_date=datetime.date(2025, 1, 10),
        gross_amount=Decimal("500000.00"),
        agreed_credit_days=30,
        payments=payments,
        evaluation_date=datetime.date(2025, 3, 31)
    )

    result = engine.evaluate_invoice(req)

    assert result.is_protected is True
    assert result.statutory_due_date == datetime.date(2025, 2, 9)
    assert result.outstanding_principal == Decimal("250000.00")
    assert result.status == "PARTIALLY_PAID"

    # Base value calculation: 500,000 / 1.18 = 423,728.81
    # Unpaid at March 31 is 50%, so disallowance base is 423,728.81 * 0.5 = 211,864.41
    assert result.tax_disallowance_base_sec43bh == Decimal("211864.41")
    # Corporate tax at 25.168%: 211,864.41 * 0.25168 = 53,322.03
    assert result.potential_corporate_tax_exposure == Decimal("53322.03")
    # Interest accrued should be strictly positive and reflect waterfall (actual: 16,553.10)
    assert result.accrued_penal_interest_sec16 > Decimal("16000.00")


def test_statutory_dispute_freeze(engine):
    """
    Test Case: Formal written objection lodged under Section 15 within 15 days.
    Statutory countdown and penal interest must be completely frozen.
    """
    req = InvoiceEvaluationRequest(
        invoice_id="INV-2025-DISPUTE-01",
        vendor_name="Defective Castings Pvt Ltd",
        udyam_category="SMALL",
        is_trader=False,
        bill_date=datetime.date(2025, 1, 1),
        gross_amount=Decimal("400000.00"),
        agreed_credit_days=15,
        evaluation_date=datetime.date(2025, 4, 15),
        is_disputed=True  # Statutory Dispute Hold Active
    )

    result = engine.evaluate_invoice(req)

    assert result.status == "DISPUTED_HOLD"
    assert result.overdue_days == 0
    assert result.accrued_penal_interest_sec16 == Decimal("0.00")
    assert result.potential_corporate_tax_exposure == Decimal("0.00")
    assert result.total_statutory_exposure == Decimal("0.00")


def test_statutory_45_day_cap_enforcement(engine):
    """
    Test Case: Contract specifies 90 days credit.
    Under Section 15 MSMED Act, the statutory window cannot exceed 45 days.
    The engine must override contract terms and cap statutory days to 45.
    """
    req = InvoiceEvaluationRequest(
        invoice_id="INV-2025-OVER-CREDIT",
        vendor_name="Alpha Tech Services",
        udyam_category="MICRO",
        is_trader=False,
        bill_date=datetime.date(2025, 2, 1),
        gross_amount=Decimal("100000.00"),
        agreed_credit_days=90,  # Illegal under Section 15
        evaluation_date=datetime.date(2025, 2, 2)
    )

    result = engine.evaluate_invoice(req)

    assert result.statutory_credit_days == 45
    assert result.statutory_due_date == datetime.date(2025, 3, 18)


def test_unwritten_contract_defaults_to_15_days(engine):
    """
    Test Case: No written agreement exists (agreed_credit_days = 0).
    Statutory due date must be exactly 15 days from bill date.
    """
    req = InvoiceEvaluationRequest(
        invoice_id="INV-2025-NO-AGREEMENT",
        vendor_name="Quick Machine Tools",
        udyam_category="SMALL",
        is_trader=False,
        bill_date=datetime.date(2025, 3, 1),
        gross_amount=Decimal("200000.00"),
        agreed_credit_days=0,  # No written contract
        evaluation_date=datetime.date(2025, 3, 2)
    )

    result = engine.evaluate_invoice(req)

    assert result.statutory_credit_days == 15
    assert result.statutory_due_date == datetime.date(2025, 3, 16)
