# apps/api/app/services/banking_exporter.py

import re
import csv
import io
import hashlib
import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PayoutLineItem(BaseModel):
    voucher_id: str
    invoice_reference: str
    beneficiary_name: str
    beneficiary_account_no: str
    beneficiary_ifsc: str
    amount: Decimal = Field(gt=Decimal("0.00"), description="Disbursement amount in INR")
    beneficiary_email: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator("beneficiary_ifsc")
    def validate_ifsc(cls, v: str) -> str:
        clean = v.strip().upper()
        # Exactly 11 chars: 4 alpha bank code, 5th character strictly literal zero '0', 6 alphanumeric branch code
        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", clean):
            raise ValueError(f"Invalid IFSC code format: '{clean}'. Must be 11 characters with '0' as 5th character.")
        return clean

    @field_validator("beneficiary_account_no")
    def validate_account_no(cls, v: str) -> str:
        clean = re.sub(r"[\s\-]", "", v.strip())
        # 9 to 34 characters (alphanumeric allowed for virtual accounts)
        if not re.match(r"^[A-Za-z0-9]{9,34}$", clean):
            raise ValueError(f"Invalid account number: '{clean}'. Must be between 9 and 34 alphanumeric characters.")
        return clean

    @field_validator("amount", mode="before")
    def parse_amount(cls, v):
        return Decimal(str(v))


class BatchExportResult(BaseModel):
    batch_reference: str
    bank_rail: str
    record_count: int
    total_disbursement_amount: Decimal
    file_name: str
    file_content_csv: str
    file_checksum_sha256: str


class BankingBatchExporter:
    """
    Production Batch Payment Exporter for ICICI Corporate Internet Banking (CIB)
    and HDFC ENet. Enforces zero-shift two-pass text sanitization, strict column
    alignments, and SHA-256 cryptographic audit tracking.
    """

    TWO_PLACES = Decimal("0.01")

    @staticmethod
    def sanitize_text(text: Optional[str], max_len: int, allow_spaces: bool = True) -> str:
        """
        Two-Pass Sanitizer:
        Pass 1: Strip control characters, quotes, commas, semicolons, and delimiters
                to eliminate CSV column shifts in bank legacy mainframes.
        Pass 2: Whitelist alphanumeric characters and convert strictly to uppercase.
        """
        if not text:
            return ""

        # Pass 1: Replace commas, semicolons, and slashes with single space
        s = re.sub(r'[,;/]', " ", str(text))

        # Strip quotes, parens, brackets, and special symbols directly without extra spaces
        s = re.sub(r'[\'\"\\&%#@!\$\*\<\>\?=\+\(\)\[\]\{\}]', "", s)

        # Pass 2: Filter strictly to alphanumeric, hyphens, underscores, and single spaces
        if allow_spaces:
            s = re.sub(r"[^A-Za-z0-9\-\s_]", "", s)
            s = re.sub(r"\s+", " ", s).strip()
        else:
            s = re.sub(r"[^A-Za-z0-9\-_]", "", s).strip()

        return s.upper()[:max_len]

    @classmethod
    def generate_icici_cib_batch(
        cls,
        batch_seq: int,
        client_debit_account: str,
        items: List[PayoutLineItem],
        value_date: Optional[datetime.date] = None,
    ) -> BatchExportResult:
        """
        Generates standard ICICI Corporate Internet Banking (CIB) Bulk Upload CSV.
        Template: PAB_VENDOR (11 Mandatory/Standard Columns)
        """
        if not items:
            raise ValueError("Cannot generate payment batch with zero records.")

        d_val = value_date or datetime.date.today()
        date_formatted = d_val.strftime("%d/%m/%Y")
        date_file_str = d_val.strftime("%d%m%Y")

        clean_debit_acc = cls.sanitize_text(client_debit_account, 18, allow_spaces=False)
        batch_ref = f"ICICI-{date_file_str}-{batch_seq:03d}"
        file_name = f"{clean_debit_acc[:8]}_{date_file_str}_{batch_seq:02d}.csv"

        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=",",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n",
        )

        total_amount = Decimal("0.00")

        for item in items:
            quantized_amt = item.amount.quantize(cls.TWO_PLACES, rounding=ROUND_HALF_UP)
            total_amount += quantized_amt

            # Mode selection rule: RTGS for >= 200,000; NEFT for lower
            payment_mode = "RTGS" if quantized_amt >= Decimal("200000.00") else "NFT"

            bene_name_clean = cls.sanitize_text(item.beneficiary_name, 50)
            narration_clean = cls.sanitize_text(
                item.remarks or f"INV {item.invoice_reference} 43BH CLR",
                50,
            )
            email_clean = item.beneficiary_email.strip() if item.beneficiary_email else ""

            # ICICI CIB Column Layout (11 Columns):
            # 1. Product Type Code ("PAB_VENDOR")
            # 2. Payment Mode ("NFT" / "RTGS")
            # 3. Debit Account Number
            # 4. Beneficiary Name
            # 5. Beneficiary Account Number
            # 6. Beneficiary IFSC Code
            # 7. Amount (Formatted to 2 decimals, zero-padded, no commas)
            # 8. Currency ("INR")
            # 9. Payment Date ("DD/MM/YYYY")
            # 10. Remarks / Narration
            # 11. Beneficiary Email
            writer.writerow([
                "PAB_VENDOR",
                payment_mode,
                clean_debit_acc,
                bene_name_clean,
                item.beneficiary_account_no,
                item.beneficiary_ifsc,
                f"{quantized_amt:.2f}",
                "INR",
                date_formatted,
                narration_clean,
                email_clean,
            ])

        csv_content = output.getvalue()
        output.close()

        # Compute SHA-256 cryptographic checksum
        checksum = hashlib.sha256(csv_content.encode("utf-8")).hexdigest()

        return BatchExportResult(
            batch_reference=batch_ref,
            bank_rail="ICICI_CIB",
            record_count=len(items),
            total_disbursement_amount=total_amount.quantize(cls.TWO_PLACES),
            file_name=file_name,
            file_content_csv=csv_content,
            file_checksum_sha256=checksum,
        )

    @classmethod
    def generate_hdfc_enet_batch(
        cls,
        batch_seq: int,
        client_code: str,
        items: List[PayoutLineItem],
        value_date: Optional[datetime.date] = None,
    ) -> BatchExportResult:
        """
        Generates standard HDFC ENet Corporate Bulk Payment CSV (10 Columns).
        """
        if not items:
            raise ValueError("Cannot generate payment batch with zero records.")

        d_val = value_date or datetime.date.today()
        date_formatted = d_val.strftime("%d/%m/%Y")
        date_file_str = d_val.strftime("%d%m")

        clean_client_code = cls.sanitize_text(client_code, 15, allow_spaces=False)
        batch_ref = f"HDFC-{d_val.strftime('%Y%m%d')}-{batch_seq:03d}"
        file_name = f"{clean_client_code[:8]}{date_file_str}.{batch_seq:03d}"

        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=",",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n",
        )

        total_amount = Decimal("0.00")

        for idx, item in enumerate(items, start=1):
            quantized_amt = item.amount.quantize(cls.TWO_PLACES, rounding=ROUND_HALF_UP)
            total_amount += quantized_amt

            payment_mode = "RTGS" if quantized_amt >= Decimal("200000.00") else "NEFT"
            bene_name_clean = cls.sanitize_text(item.beneficiary_name, 40)

            # Customer reference: Max 15 alphanumeric characters
            cust_ref = cls.sanitize_text(f"VC{date_file_str}{idx:04d}", 15, allow_spaces=False)

            narration_clean = cls.sanitize_text(
                item.remarks or f"MSME CLR {item.invoice_reference}",
                140,
            )

            # HDFC ENet Column Layout (10 Columns):
            # 1. Transaction Type ("NEFT" / "RTGS")
            # 2. Beneficiary Account Number
            # 3. Transaction Amount (Decimal formatted)
            # 4. Beneficiary Name
            # 5. Drawee Location ("PAR")
            # 6. Customer Reference Number
            # 7. Beneficiary IFSC Code
            # 8. Client Code
            # 9. Value Date ("DD/MM/YYYY")
            # 10. Remarks / Narration
            writer.writerow([
                payment_mode,
                item.beneficiary_account_no,
                f"{quantized_amt:.2f}",
                bene_name_clean,
                "PAR",
                cust_ref,
                item.beneficiary_ifsc,
                clean_client_code,
                date_formatted,
                narration_clean,
            ])

        csv_content = output.getvalue()
        output.close()

        checksum = hashlib.sha256(csv_content.encode("utf-8")).hexdigest()

        return BatchExportResult(
            batch_reference=batch_ref,
            bank_rail="HDFC_ENET",
            record_count=len(items),
            total_disbursement_amount=total_amount.quantize(cls.TWO_PLACES),
            file_name=file_name,
            file_content_csv=csv_content,
            file_checksum_sha256=checksum,
        )
