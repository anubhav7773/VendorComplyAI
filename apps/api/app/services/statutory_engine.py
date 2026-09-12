# apps/api/app/services/statutory_engine.py

import calendar
import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from app.schemas.statutory import (
    InvoiceEvaluationRequest,
    InvoiceEvaluationResponse,
    PaymentItemSchema,
)


class MSMEStatutoryEngine:
    """
    Production-grade Statutory Compliance Calculation Engine.
    Enforces Section 43B(h) Income-tax Act, 1961 & MSMED Act, 2006.
    Strictly zero floating-point arithmetic (all operations use decimal.Decimal).
    """

    TWO_PLACES = Decimal("0.01")
    FOUR_PLACES = Decimal("0.0001")

    def __init__(
        self,
        corporate_tax_rate: Decimal = Decimal("0.25168"),
        gst_rate_percent: Decimal = Decimal("18.0"),
        rbi_bank_rate: Decimal = Decimal("0.0650"),
    ):
        self.corporate_tax_rate = corporate_tax_rate
        self.gst_rate = gst_rate_percent
        self.rbi_bank_rate = rbi_bank_rate
        # Statutory penal interest rate under MSMED Section 16 is 3x RBI Bank Rate
        self.penal_annual_rate = (self.rbi_bank_rate * Decimal("3.0")).quantize(self.FOUR_PLACES)

    @staticmethod
    def is_trader_by_nic(nic_codes: List[str], is_trader_flag: bool) -> bool:
        """
        Under Ministry of MSME OM No. 5/2(2)/2021-E/P and OM No. 1/4(1)/2021-P&G,
        Wholesale and Retail traders (NIC 45, 46, 47) are restricted to PSL benefits only.
        They are excluded from MSMED Chapter V and Section 43B(h) tax disallowances.
        """
        if is_trader_flag:
            return True
        for code in nic_codes:
            cleaned = str(code).strip()
            if cleaned.startswith(("45", "46", "47")):
                return True
        return False

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """Returns exact calendar days in month, correctly handling leap years."""
        return calendar.monthrange(year, month)[1]

    def evaluate_invoice(self, req: InvoiceEvaluationRequest) -> InvoiceEvaluationResponse:
        d_eval = req.evaluation_date or datetime.date.today()
        c_tax_rate = req.corporate_tax_rate or self.corporate_tax_rate
        g_rate = req.gst_rate_percent or self.gst_rate

        # 1. Statutory Trader Exemption Check (OM 2021)
        is_trader = self.is_trader_by_nic(req.nic_codes, req.is_trader)
        is_micro_small = req.udyam_category.upper() in ["MICRO", "SMALL"]
        
        # Protection applies strictly to Micro & Small Manufacturers/Service Providers
        is_protected = is_micro_small and (not is_trader)

        # 2. Section 15 Statutory Credit Deadline Calculation
        if req.agreed_credit_days > 0:
            statutory_credit_days = min(req.agreed_credit_days, 45)
        else:
            statutory_credit_days = 15

        statutory_due_date = req.bill_date + datetime.timedelta(days=statutory_credit_days)

        # 3. Base Amount Calculation (Excludes GST if ITC claimed)
        if req.gst_claimed_as_itc:
            gst_divisor = Decimal("1.0") + (g_rate / Decimal("100.0"))
            taxable_base = (req.gross_amount / gst_divisor).quantize(
                self.TWO_PLACES, rounding=ROUND_HALF_UP
            )
        else:
            taxable_base = req.gross_amount.quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)

        # 4. Payments Waterfall & Settlement Chronology
        sorted_payments = sorted(req.payments, key=lambda x: x.payment_date)
        total_paid = sum((p.amount for p in sorted_payments), Decimal("0.00")).quantize(self.TWO_PLACES)
        outstanding_principal = max(Decimal("0.00"), req.gross_amount - total_paid).quantize(self.TWO_PLACES)

        # 5. Overdue Status & Aging Days
        overdue_days = 0
        if d_eval > statutory_due_date and outstanding_principal > Decimal("0.00") and not req.is_disputed:
            overdue_days = (d_eval - statutory_due_date).days
        is_overdue = overdue_days > 0

        # 6. Section 16 Monthly Compounding Penal Interest Calculation
        accrued_penal_interest = Decimal("0.00")
        monthly_rate = self.penal_annual_rate / Decimal("12.0")

        # Interest only accrues if protected, overdue, and not in dispute freeze
        if is_protected and is_overdue and not req.is_disputed:
            current_date = statutory_due_date + datetime.timedelta(days=1)
            compounding_principal = req.gross_amount
            remaining_payments = [PaymentItemSchema(payment_date=p.payment_date, amount=p.amount) for p in sorted_payments]

            while current_date <= d_eval and compounding_principal > Decimal("0.00"):
                c_year, c_month = current_date.year, current_date.month
                days_in_month = self.get_days_in_month(c_year, c_month)
                month_end_date = datetime.date(c_year, c_month, days_in_month)

                # Check if any payments occurred during this active rest window
                applicable_payments = [
                    p for p in remaining_payments
                    if p.payment_date >= current_date and p.payment_date <= min(month_end_date, d_eval)
                ]

                if applicable_payments:
                    next_pay = applicable_payments[0]
                    p_date = next_pay.payment_date
                    p_amt = next_pay.amount

                    elapsed_days = (p_date - current_date).days
                    if elapsed_days > 0:
                        fractional_factor = Decimal(elapsed_days) / Decimal(days_in_month)
                        interest_segment = compounding_principal * monthly_rate * fractional_factor
                        accrued_penal_interest += interest_segment

                    # Waterfall Principal Reduction
                    compounding_principal = max(Decimal("0.00"), compounding_principal - p_amt)
                    current_date = p_date + datetime.timedelta(days=1)
                    remaining_payments.remove(next_pay)
                    continue

                if d_eval >= month_end_date:
                    # Full month compounding rest
                    month_interest = compounding_principal * monthly_rate
                    accrued_penal_interest += month_interest
                    compounding_principal += month_interest  # Add to base for next compounding rest
                    current_date = month_end_date + datetime.timedelta(days=1)
                else:
                    # Final partial month
                    remaining_days = (d_eval - current_date).days + 1
                    if remaining_days > 0:
                        fractional_factor = Decimal(remaining_days) / Decimal(days_in_month)
                        accrued_penal_interest += compounding_principal * monthly_rate * fractional_factor
                    break

        accrued_penal_interest = accrued_penal_interest.quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)

        # 7. Section 43B(h) Corporate Tax Disallowance Exposure
        # Disallowance occurs if unpaid at the end of the financial year (March 31)
        fy_end_year = req.bill_date.year if req.bill_date.month <= 3 else req.bill_date.year + 1
        fy_end_date = datetime.date(fy_end_year, 3, 31)

        disallowance_base = Decimal("0.00")
        tax_disallowance_exposure = Decimal("0.00")

        if is_protected and not req.is_disputed:
            paid_by_fy_end = sum(
                (p.amount for p in sorted_payments if p.payment_date <= fy_end_date),
                Decimal("0.00"),
            )
            unpaid_at_fy_end = max(Decimal("0.00"), req.gross_amount - paid_by_fy_end)

            # Trigger condition: Due date arrived on or before March 31, and remained unpaid at March 31
            if statutory_due_date <= fy_end_date and unpaid_at_fy_end > Decimal("0.00"):
                unpaid_ratio = unpaid_at_fy_end / req.gross_amount
                disallowance_base = (taxable_base * unpaid_ratio).quantize(
                    self.TWO_PLACES, rounding=ROUND_HALF_UP
                )
                tax_disallowance_exposure = (disallowance_base * c_tax_rate).quantize(
                    self.TWO_PLACES, rounding=ROUND_HALF_UP
                )

        # 8. Operational Status Categorization
        if req.is_disputed:
            status_label = "DISPUTED_HOLD"
        elif outstanding_principal == Decimal("0.00"):
            status_label = "PAID"
        elif total_paid > Decimal("0.00"):
            status_label = "PARTIALLY_PAID"
        else:
            status_label = "UNPAID"

        # 9. Total Out-of-Pocket Statutory Exposure
        total_exposure = (tax_disallowance_exposure + accrued_penal_interest).quantize(self.TWO_PLACES)

        return InvoiceEvaluationResponse(
            invoice_id=req.invoice_id,
            vendor_name=req.vendor_name,
            udyam_category=req.udyam_category.upper(),
            is_trader=is_trader,
            is_protected=is_protected,
            bill_date=req.bill_date,
            statutory_credit_days=statutory_credit_days,
            statutory_due_date=statutory_due_date,
            gross_amount=req.gross_amount.quantize(self.TWO_PLACES),
            taxable_base_amount=taxable_base,
            total_paid=total_paid,
            outstanding_principal=outstanding_principal,
            overdue_days=overdue_days,
            is_overdue=is_overdue,
            effective_annual_penal_rate=(self.penal_annual_rate * Decimal("100.0")).quantize(self.TWO_PLACES),
            accrued_penal_interest_sec16=accrued_penal_interest,
            tax_disallowance_base_sec43bh=disallowance_base,
            potential_corporate_tax_exposure=tax_disallowance_exposure,
            total_statutory_exposure=total_exposure,
            status=status_label,
        )
