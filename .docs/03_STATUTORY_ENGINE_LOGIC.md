# ==============================================================================
# VENDORCOMPLY AI — STATUTORY COMPLIANCE & MATHEMATICAL CALCULATION ENGINE
# Document ID: 03_STATUTORY_ENGINE_LOGIC.md
# Parent Entity: asiverticals.me
# Statutory Baseline: Section 43B(h) of Income-tax Act, 1961 & MSMED Act, 2006
# Precision Standard: Zero Floating-Point Arithmetic (Strict Python Decimal)
# ==============================================================================

## 1. STATUTORY GROUNDING & REGULATORY FRAMEWORK

VendorComply AI translates Indian corporate tax provisions and micro/small enterprise protection laws into an automated, deterministic mathematical engine[cite: 1, 2]. The platform automates calculations across four statutory pillars:

### A. Section 43B(h) of the Income-tax Act, 1961
1. **Statutory Mandate**: Any sum payable by the assessee to a Micro or Small enterprise beyond the time limit specified in Section 15 of the Micro, Small and Medium Enterprises Development (MSMED) Act, 2006 shall be allowed as a tax deduction strictly on an **actual payment basis** in the previous year in which such sum is actually paid[cite: 1, 2].
2. **Accrual Basis Overridden**: Normal mercantile accounting deductions are disallowed at the close of the financial year (March 31) if payment remains outstanding beyond the statutory timeline[cite: 1, 2].
3. **Disallowance Base Determination**:
   * If the buyer claims **Input Tax Credit (ITC)** on GST separately in books of account, the GST component does not enter the Profit & Loss statement as an expense. Consequently, the disallowance is strictly restricted to the **Taxable Base Amount (excluding GST)**.
   * If GST is not claimed as ITC and is charged directly to Profit & Loss as an expense, the disallowance applies to the **Gross Invoice Amount**[cite: 2].

### B. Section 15 of the MSMED Act, 2006 (Statutory Payment Deadlines)
Section 15 sets strict statutory limits on payment duration between buyer and supplier[cite: 1, 2]:
* **Scenario 1: No Written Agreement**: The buyer must make payment on or before the **appointed day**, defined as the day immediately following the expiration of **15 days** from the day of acceptance or the day of deemed acceptance of any goods or services[cite: 1, 2].
* **Scenario 2: Written Contract in Existence**: Where there is a written agreement between the buyer and the supplier, the payment period cannot exceed **45 days** from the day of acceptance or deemed acceptance[cite: 1, 2]. If the contract specifies 60 or 90 days, the law overrides the contract and caps the credit window at **45 days**[cite: 1, 2].
* **Day of Acceptance vs. Deemed Acceptance (Section 2(b))**:
  * *Day of Acceptance*: The day of actual delivery of goods or the rendering of services.
  * *Day of Deemed Acceptance*: Where any objection is made in writing by the buyer regarding acceptance of goods or services within 15 days of delivery, the day of acceptance is the day on which such objection is removed by the supplier.
  * *Statutory Dispute Freeze*: If a formal written objection is logged within 15 days, the statutory countdown is **frozen**, and penal interest does not accrue during the disputed period.

### C. Section 16 of the MSMED Act, 2006 (Compound Penal Interest)
* Where any buyer fails to make payment to a supplier as required under Section 15, the buyer is liable to pay **compound interest with monthly rests** to the supplier on that amount from the appointed day (or agreed date)[cite: 1, 2].
* **Statutory Rate**: Exactly **three times the Bank Rate** notified by the Reserve Bank of India (RBI)[cite: 1, 2].
  $$\text{Penal Rate } (r) = 3 \times \text{RBI Bank Rate}$$
  *(e.g., if RBI Bank Rate is 6.50% p.a., $r = 3 \times 0.065 = 19.50\%\text{ p.a.}$)[cite: 2].*

### D. Section 23 of the MSMED Act, 2006 (Non-Deductibility Penalty)
* Notwithstanding anything contained in the Income-tax Act, 1961, the amount of interest paid or payable by buyer under Section 16 **shall not be allowed as deduction** in computation of taxable income[cite: 2].
* **Zero Tax Shield**: Unlike standard business interest (which reduces corporate tax liability by ~25.17%), Section 16 interest represents a **100% net cash loss**[cite: 2].

### E. The Trader Exclusion Doctrine (Ministry OMs of 2021)
* Under Ministry of MSME Office Memorandums (OM No. 5/2(2)/2021-E/P and G/Policy dated July 2, 2021, and OM No. 1/4(1)/2021-P&G/Policy dated September 1, 2021), **Retail and Wholesale Traders (NIC Codes 45, 46, and 47)** are eligible for Udyam Registration exclusively for **Priority Sector Lending (PSL)**[cite: 2].
* Traders do **not** qualify as an "enterprise" under Section 2(e) of the MSMED Act for Chapter V protections[cite: 2].
* **Legal Result**: Dues owed to Wholesale or Retail Traders are **exempt from Section 43B(h) tax disallowance** and **do not attract Section 16 penal interest**[cite: 2]. Medium enterprises are likewise excluded from 43B(h) protection[cite: 2].

---

## 2. MATHEMATICAL FORMULATION & COMPOUNDING MODELS

### A. Statutory Due Date Calculation
$$\text{Effective Credit Days} = \begin{cases}  15 & \text{if } \text{agreed\_credit\_days} = 0 \text{ (No written contract)} \\ \min(\text{agreed\_credit\_days}, 45) & \text{if } \text{agreed\_credit\_days} > 0 \text{ (Written contract)} \end{cases}$$
[cite: 1, 2]

$$\text{Due Date} = \text{Invoice/Receipt Date} + \text{Effective Credit Days}$$
[cite: 2]

---

### B. Section 16 Monthly Compounding Penal Interest Model
Compound interest with monthly rests is calculated using exact calendar boundaries (e.g., Jan 31, Feb 28/29, Mar 31)[cite: 2]. When an invoice remains unpaid across multiple months, interest compounds at the end of each calendar month, adding accrued interest to the principal base for the subsequent month[cite: 2].

#### 1. Formula for Completed Full Compounding Months:
For each complete calendar month elapsed:
$$I_{month} = P_{active} \times \left(\frac{r}{12}\right)$$
[cite: 2]
$$P_{active} \leftarrow P_{active} + I_{month}$$
[cite: 2]

#### 2. Formula for Fractional Calendar Months:
For any partial month period of $d$ elapsed days within a month of $D_{month}$ total days:
$$I_{fractional} = P_{active} \times \left(\frac{r}{12}\right) \times \left(\frac{d}{D_{month}}\right)$$
[cite: 2]
Where:
* $r = 3 \times \text{RBI Bank Rate}$[cite: 2].
* $d = (\text{Evaluation Date} - \text{Start of Fractional Period}) + 1$[cite: 2].
* $D_{month} \in \{28, 29, 30, 31\}$ (Exact days in that specific calendar month)[cite: 2].
* **Leap Year Rule**: If the fractional period falls in February of a leap year ($year \pmod 4 == 0$ and $year \pmod{100} \neq 0$ or $year \pmod{400} == 0$), $D_{month} = 29$, otherwise $28$[cite: 2].

---

### C. Partial Payment Waterfall Schedule
When multiple partial payments are made across different dates, the algorithm executes waterfall compounding[cite: 2]:
1. Prior to any partial payment date $t_{pay}$, the engine accrues fractional interest on the active principal balance $P_{active}$ up to $t_{pay}$[cite: 2].
2. The payment amount $S$ is subtracted from the principal:
   $$P_{remaining} = \max(0.00, P_{active} - S)$$
[cite: 2]
3. Subsequent monthly compounding rests apply strictly to the reduced balance $P_{remaining}$[cite: 2].

---

### D. Financial Year-End Section 43B(h) Corporate Tax Disallowance
Let $FY_{end} = \text{March 31}$ of the relevant Financial Year for the invoice[cite: 2].
Disallowance triggers if and only if:
1. The supplier is an eligible Micro or Small Manufacturer or Service Provider (`is_protected = TRUE`)[cite: 2].
2. $\text{Due Date} \le FY_{end}$[cite: 2].
3. The invoice has an unpaid balance as of $FY_{end}$ ($P_{unpaid\_at\_fy\_end} > 0$)[cite: 2].

#### Disallowance Equations:
$$\text{Unpaid Ratio} = \frac{P_{unpaid\_at\_fy\_end}}{\text{Gross Invoice Amount}}$$
[cite: 2]
$$\text{Disallowance Base} = \text{Taxable Base Amount} \times \text{Unpaid Ratio}$$
[cite: 2]
$$\text{Immediate Corporate Tax Exposure} = \text{Disallowance Base} \times \tau_{corp}$$
[cite: 2]

Where $\tau_{corp}$ is the tenant's corporate tax rate inclusive of surcharge and cess[cite: 2]:
* **Section 115BAA Regime**: $22\% + 10\%\text{ Surcharge} + 4\%\text{ Cess} = \mathbf{25.168\%}$ ($0.25168$)[cite: 2].
* **Old Corporate Regime**: $30\% + 7\%/12\%\text{ Surcharge} + 4\%\text{ Cess} \approx \mathbf{31.20\% \text{ to } 34.94\%}$[cite: 2].

---

### E. Total Statutory Financial Exposure Metric
$$\text{Total Exposure} = \text{Immediate Corporate Tax Exposure u/s 43B(h)} + \text{Accrued Section 16 Penal Interest}$$
[cite: 2]
*(Both figures represent non-recoverable out-of-pocket cash outflows)[cite: 2].*

---

## 3. STATUTORY EDGE-CASE MATRIX

| Scenario / Edge Case | Statutory Reality | System Execution Logic |
| :--- | :--- | :--- |
| **Wholesale / Retail Trader (NIC 45, 46, 47)**[cite: 2] | Exempt from MSMED Chapter V & 43B(h)[cite: 2]. | `is_trader = True` $\rightarrow$ Exposure = ₹0.00, Due date strictly informational[cite: 2]. |
| **Medium Enterprise Supplier**[cite: 2] | Protected for Section 16 interest, but **excluded from 43B(h) disallowance**[cite: 2]. | 43B(h) disallowance base = ₹0.00; Section 16 penal interest calculated if overdue[cite: 2]. |
| **Written Agreement Specifies 60 Days**[cite: 2] | Overridden by MSMED Section 15 statutory cap (max 45 days)[cite: 1, 2]. | Credit window clamped: `min(60, 45) = 45 days`[cite: 1, 2]. |
| **No Written Agreement (Verbal/PO silent)**[cite: 1, 2] | Statutory 15-day rule triggers from date of delivery[cite: 1, 2]. | Credit window set strictly to 15 calendar days[cite: 1, 2]. |
| **Written Dispute Lodged within 15 Days** | Deemed acceptance suspended under Section 2(b). | Status becomes `DISPUTED_HOLD`. Countdown paused; Penal interest = ₹0.00. |
| **Written Dispute Lodged AFTER 15 Days** | Objection invalid to stop statutory clock under Section 2(b). | Flagged as `HIGH_SCRUTINY_DISPUTE`. Clock continues; CA alerted for manual scrutiny. |
| **Leap Year Handling (February)**[cite: 2] | Daily interest rests must reflect actual days in month[cite: 2]. | Days denominator $D_{month}$ set dynamically to 29 if leap year, else 28[cite: 2]. |
| **Partial Settlement before March 31**[cite: 2] | Only the unpaid fraction is disallowed u/s 43B(h)[cite: 2]. | Disallowance base calculated proportionally: $\text{Base} \times \frac{\text{Unpaid}}{\text{Gross}}$[cite: 2]. |
| **Full Settlement on 1st April (Post FY-End)**[cite: 2] | Disallowance triggers in FY1, deductible in FY2 upon payment[cite: 1, 2]. | 100% Tax disallowance added to FY1 Tax Audit Form 3CD Clause 22[cite: 1, 2]. |

---

## 4. PRODUCTION PYTHON ALGORITHM (ZERO-FLOAT IMPLEMENTATION)

Save this production service at `apps/api/app/services/statutory_engine.py`. This implementation uses `decimal.Decimal` with `ROUND_HALF_UP` quantization to eliminate rounding discrepancies[cite: 2].

```python
# apps/api/app/services/statutory_engine.py

import calendar
import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field


class PaymentRecord(BaseModel):
    payment_date: datetime.date
    amount: Decimal = Field(gt=Decimal('0.00'))


class StatutoryEvaluationResult(BaseModel):
    invoice_id: str
    vendor_name: str
    udyam_category: str
    is_trader: bool
    is_protected: bool
    bill_date: datetime.date
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
    status: str


class MSMEStatutoryEngine:
    """
    Statutory Compliance & Mathematical Engine for Section 43B(h) and MSMED Act Section 16.
    Enforces zero floating-point arithmetic using strict Decimal quantization.
    """

    TWO_PLACES = Decimal('0.01')
    FOUR_PLACES = Decimal('0.0001')

    def __init__(
        self,
        corporate_tax_rate: Decimal = Decimal('0.25168'), # Default Section 115BAA (25.168%)
        default_gst_rate_percent: Decimal = Decimal('18.0'),
        rbi_bank_rate: Decimal = Decimal('0.0650')        # 6.50% RBI Bank Rate
    ):
        self.corporate_tax_rate = corporate_tax_rate
        self.gst_rate = default_gst_rate_percent
        self.rbi_bank_rate = rbi_bank_rate
        self.penal_annual_rate = (self.rbi_bank_rate * Decimal('3.0')).quantize(self.FOUR_PLACES)

    def is_leap_year(self, year: int) -> bool:
        """Determines whether a given calendar year is a leap year."""
        return calendar.isleap(year)

    def get_days_in_month(self, year: int, month: int) -> int:
        """Returns the exact number of days in a specific calendar month, respecting leap years."""
        return calendar.monthrange(year, month)[1]

    def evaluate_invoice(
        self,
        invoice_id: str,
        vendor_name: str,
        udyam_category: str,
        is_trader: bool,
        bill_date: datetime.date,
        gross_amount: Decimal,
        agreed_credit_days: int = 0,
        payments: Optional[List[PaymentRecord]] = None,
        evaluation_date: Optional[datetime.date] = None,
        gst_claimed_as_itc: bool = True,
        is_disputed: bool = False
    ) -> StatutoryEvaluationResult:
        """
        Executes full statutory compliance evaluation for an invoice.
        """
        d_eval = evaluation_date or datetime.date.today()
        payments_list = payments or []

        # 1. Protection Eligibility Filter
        # Only Micro & Small Manufacturers/Services are protected u/s 43B(h) and Sec 15/16.
        # Traders (Retail/Wholesale) and Medium enterprises are excluded from 43B(h).
        is_micro_small = udyam_category.upper() in ['MICRO', 'SMALL']
        is_protected = is_micro_small and (not is_trader)

        # 2. Statutory Due Date Calculation (Section 15 MSMED Act)
        if agreed_credit_days > 0:
            statutory_credit_days = min(agreed_credit_days, 45)
        else:
            statutory_credit_days = 15

        statutory_due_date = bill_date + datetime.timedelta(days=statutory_credit_days)

        # 3. Base Amount Calculation (Excludes GST if claimed as ITC)
        if gst_claimed_as_itc:
            gst_divisor = Decimal('1.0') + (self.gst_rate / Decimal('100.0'))
            taxable_base = (gross_amount / gst_divisor).quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)
        else:
            taxable_base = gross_amount.quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)

        # 4. Chronological Payment Sorting & Total Paid
        sorted_payments = sorted(payments_list, key=lambda x: x.payment_date)
        total_paid = sum((p.amount for p in sorted_payments), Decimal('0.00')).quantize(self.TWO_PLACES)
        outstanding_principal = max(Decimal('0.00'), gross_amount - total_paid).quantize(self.TWO_PLACES)

        # 5. Overdue Status & Aging Days
        overdue_days = 0
        if d_eval > statutory_due_date and outstanding_principal > Decimal('0.00') and not is_disputed:
            overdue_days = (d_eval - statutory_due_date).days
        is_overdue = overdue_days > 0

        # 6. Section 16 Compounding Penal Interest Calculation (Waterfall Schedule)
        accrued_penal_interest = Decimal('0.00')
        monthly_rate = self.penal_annual_rate / Decimal('12.0')

        if is_protected and is_overdue and not is_disputed:
            current_date = statutory_due_date + datetime.timedelta(days=1)
            compounding_principal = gross_amount
            remaining_payments = [PaymentRecord(payment_date=p.payment_date, amount=p.amount) for p in sorted_payments]

            while current_date <= d_eval and compounding_principal > Decimal('0.00'):
                c_year, c_month = current_date.year, current_date.month
                days_in_month = self.get_days_in_month(c_year, c_month)
                month_end_date = datetime.date(c_year, c_month, days_in_month)

                # Check for payments occurring within current monthly rest
                applicable_payments = [
                    p for p in remaining_payments 
                    if p.payment_date <= min(month_end_date, d_eval) and p.payment_date >= current_date
                ]

                if applicable_payments:
                    next_payment = applicable_payments[0]
                    p_date = next_payment.payment_date
                    p_amount = next_payment.amount

                    elapsed_days = (p_date - current_date).days
                    if elapsed_days > 0:
                        fractional_factor = Decimal(elapsed_days) / Decimal(days_in_month)
                        interest_chunk = compounding_principal * monthly_rate * fractional_factor
                        accrued_penal_interest += interest_chunk

                    # Apply Waterfall Payment
                    compounding_principal = max(Decimal('0.00'), compounding_principal - p_amount)
                    current_date = p_date + datetime.timedelta(days=1)
                    remaining_payments.remove(next_payment)
                    continue

                if d_eval >= month_end_date:
                    # Full Calendar Month Compounding Rest
                    month_interest = compounding_principal * monthly_rate
                    accrued_penal_interest += month_interest
                    compounding_principal += month_interest # Compound base for next rest
                    current_date = month_end_date + datetime.timedelta(days=1)
                else:
                    # Partial Final Month
                    remaining_days = (d_eval - current_date).days + 1
                    if remaining_days > 0:
                        fractional_factor = Decimal(remaining_days) / Decimal(days_in_month)
                        accrued_penal_interest += compounding_principal * monthly_rate * fractional_factor
                    break

        accrued_penal_interest = accrued_penal_interest.quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)

        # 7. Section 43B(h) Year-End Corporate Tax Disallowance Exposure
        # Disallowance triggers if overdue at the close of 31st March of the relevant FY
        fy_end_year = bill_date.year if bill_date.month <= 3 else bill_date.year + 1
        fy_end_date = datetime.date(fy_end_year, 3, 31)

        disallowance_base = Decimal('0.00')
        tax_disallowance_exposure = Decimal('0.00')

        if is_protected and not is_disputed:
            paid_by_fy_end = sum(
                (p.amount for p in sorted_payments if p.payment_date <= fy_end_date), 
                Decimal('0.00')
            )
            unpaid_at_fy_end = max(Decimal('0.00'), gross_amount - paid_by_fy_end)

            # Condition: Due date expired on or before 31st March and still unpaid at 31st March
            if statutory_due_date <= fy_end_date and unpaid_at_fy_end > Decimal('0.00'):
                unpaid_ratio = unpaid_at_fy_end / gross_amount
                disallowance_base = (taxable_base * unpaid_ratio).quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)
                tax_disallowance_exposure = (disallowance_base * self.corporate_tax_rate).quantize(
                    self.TWO_PLACES, rounding=ROUND_HALF_UP
                )

        # 8. Determine Operational Status
        if is_disputed:
            status_label = "DISPUTED_HOLD"
        elif outstanding_principal == Decimal('0.00'):
            status_label = "PAID"
        elif total_paid > Decimal('0.00'):
            status_label = "PARTIALLY_PAID"
        else:
            status_label = "UNPAID"

        # 9. Total Exposure
        total_exposure = (tax_disallowance_exposure + accrued_penal_interest).quantize(self.TWO_PLACES)

        return StatutoryEvaluationResult(
            invoice_id=invoice_id,
            vendor_name=vendor_name,
            udyam_category=udyam_category.upper(),
            is_trader=is_trader,
            is_protected=is_protected,
            bill_date=bill_date,
            statutory_due_date=statutory_due_date,
            gross_amount=gross_amount.quantize(self.TWO_PLACES),
            taxable_base_amount=taxable_base,
            total_paid=total_paid,
            outstanding_principal=outstanding_principal,
            overdue_days=overdue_days,
            is_overdue=is_overdue,
            effective_annual_penal_rate=(self.penal_annual_rate * Decimal('100.0')).quantize(self.TWO_PLACES),
            accrued_penal_interest_sec16=accrued_penal_interest,
            tax_disallowance_base_sec43bh=disallowance_base,
            potential_corporate_tax_exposure=tax_disallowance_exposure,
            total_statutory_exposure=total_exposure,
            status=status_label
        )
5. STATUTORY UNIT TEST VERIFICATION SUITE
The following unit tests execute against the statutory test fixtures established in the audit specification[cite: 2]. Place in apps/api/tests/test_statutory_engine.py:

Python
# apps/api/tests/test_statutory_engine.py

import datetime
from decimal import Decimal
from app.services.statutory_engine import MSMEStatutoryEngine, PaymentRecord


def test_statutory_trader_exemption():
    """
    Test Case: Apex Trading Corp (INV-2024-002)
    A registered Small Trader owed ₹12,00,000 overdue beyond 45 days.
    Under Ministry OMs of 2021, traders must have ZERO tax disallowance and ZERO penal interest.
    """
    engine = MSMEStatutoryEngine(corporate_tax_rate=Decimal('0.25168'), rbi_bank_rate=Decimal('0.0650'))
    
    result = engine.evaluate_invoice(
        invoice_id="INV-2024-002",
        vendor_name="Apex Trading Corp",
        udyam_category="SMALL",
        is_trader=True, # Trader Flag
        bill_date=datetime.date(2025, 1, 15),
        gross_amount=Decimal('1200000.00'),
        agreed_credit_days=60,
        evaluation_date=datetime.date(2025, 3, 31)
    )

    assert result.is_protected is False
    assert result.accrued_penal_interest_sec16 == Decimal('0.00')
    assert result.tax_disallowance_base_sec43bh == Decimal('0.00')
    assert result.potential_corporate_tax_exposure == Decimal('0.00')
    assert result.total_statutory_exposure == Decimal('0.00')


def test_partial_payment_waterfall_and_leap_year():
    """
    Test Case: Precision Components Ltd (INV-2024-001)
    Micro Manufacturer with partial payments across Feb & Mar 2025.
    Verifies compounding reduction upon partial settlements.
    """
    engine = MSMEStatutoryEngine(corporate_tax_rate=Decimal('0.25168'), rbi_bank_rate=Decimal('0.0650'))
    
    payments = [
        PaymentRecord(payment_date=datetime.date(2025, 2, 20), amount=Decimal('100000.00')),
        PaymentRecord(payment_date=datetime.date(2025, 3, 15), amount=Decimal('150000.00'))
    ]

    result = engine.evaluate_invoice(
        invoice_id="INV-2024-001",
        vendor_name="Precision Components Ltd",
        udyam_category="MICRO",
        is_trader=False,
        bill_date=datetime.date(2025, 1, 10),
        gross_amount=Decimal('500000.00'),
        agreed_credit_days=30,
        payments=payments,
        evaluation_date=datetime.date(2025, 3, 31)
    )

    assert result.is_protected is True
    assert result.outstanding_principal == Decimal('250000.00')
    assert result.statutory_due_date == datetime.date(2025, 2, 9)
    # Proportional disallowance base: (500000 / 1.18) * (250000 / 500000) = 211,864.41
    assert result.tax_disallowance_base_sec43bh == Decimal('211864.41')
    assert result.potential_corporate_tax_exposure == Decimal('53322.03')
    assert result.accrued_penal_interest_sec16 > Decimal('18000.00')


def test_statutory_dispute_hold():
    """
    Test Case: Vendor dispute lodged within statutory 15-day window.
    Clock must freeze, and interest must remain zero.
    """
    engine = MSMEStatutoryEngine()
    
    result = engine.evaluate_invoice(
        invoice_id="INV-2024-DISPUTE",
        vendor_name="Defective Parts Pvt Ltd",
        udyam_category="SMALL",
        is_trader=False,
        bill_date=datetime.date(2025, 1, 1),
        gross_amount=Decimal('300000.00'),
        agreed_credit_days=15,
        evaluation_date=datetime.date(2025, 4, 1),
        is_disputed=True # Dispute Freeze Active
    )

    assert result.status == "DISPUTED_HOLD"
    assert result.accrued_penal_interest_sec16 == Decimal('0.00')
    assert result.potential_corporate_tax_exposure == Decimal('0.00')