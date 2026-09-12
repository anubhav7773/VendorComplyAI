# apps/api/tests/test_banking_exporter.py

import pytest
from decimal import Decimal
from pydantic import ValidationError
from app.services.banking_exporter import BankingBatchExporter, PayoutLineItem


def test_icici_cib_sanitization_and_11_columns():
    """
    Verifies ICICI CIB CSV output:
    1. Must contain strictly 11 columns.
    2. Commas and quotes in company name must be stripped to prevent column shifting.
    3. Mode must be NFT for amounts under 200,000.
    """
    dirty_name = 'Maheshwari & Sons, Plastics "Pvt" Ltd / Unit #4'
    items = [
        PayoutLineItem(
            voucher_id="v1",
            invoice_reference="INV/2026/001",
            beneficiary_name=dirty_name,
            beneficiary_account_no="123456789012",
            beneficiary_ifsc="ICIC0000002",
            amount=Decimal("150000.00"),
            remarks="Bill, Payment; 43B(h)",
            beneficiary_email="accounts@maheshwari.com"
        )
    ]

    result = BankingBatchExporter.generate_icici_cib_batch(
        batch_seq=1,
        client_debit_account="167105000250",
        items=items
    )

    lines = result.file_content_csv.strip().split("\r\n")
    assert len(lines) == 1

    columns = lines[0].split(",")
    # ICICI CIB specification strictly demands 11 columns
    assert len(columns) == 11

    # Verify column contents
    assert columns[0] == "PAB_VENDOR"
    assert columns[1] == "NFT"
    assert columns[2] == "167105000250"
    assert columns[3] == "MAHESHWARI SONS PLASTICS PVT LTD UNIT 4"
    assert "," not in columns[3]
    assert columns[4] == "123456789012"
    assert columns[5] == "ICIC0000002"
    assert columns[6] == "150000.00"
    assert columns[7] == "INR"
    assert columns[9] == "BILL PAYMENT 43BH"
    assert columns[10] == "accounts@maheshwari.com"

    # Verify SHA-256 fingerprint length (64 hex characters)
    assert len(result.file_checksum_sha256) == 64


def test_hdfc_enet_rtgs_mode_and_10_columns():
    """
    Verifies HDFC ENet CSV output:
    1. Must contain strictly 10 columns.
    2. Amounts >= 200,000 must automatically select RTGS mode.
    3. Drawee location must be set to 'PAR'.
    """
    items = [
        PayoutLineItem(
            voucher_id="v2",
            invoice_reference="INV-RTGS-99",
            beneficiary_name="Precision Heavy Tools, LLP",
            beneficiary_account_no="987654321098",
            beneficiary_ifsc="HDFC0001234",
            amount=Decimal("450000.50"),
            remarks="MSME Priority Clearance"
        )
    ]

    result = BankingBatchExporter.generate_hdfc_enet_batch(
        batch_seq=2,
        client_code="CORP_CLIENT_01",
        items=items
    )

    lines = result.file_content_csv.strip().split("\r\n")
    assert len(lines) == 1

    columns = lines[0].split(",")
    # HDFC ENet specification strictly demands 10 columns
    assert len(columns) == 10

    assert columns[0] == "RTGS"  # >= 200,000 threshold triggers RTGS
    assert columns[1] == "987654321098"
    assert columns[2] == "450000.50"
    assert columns[3] == "PRECISION HEAVY TOOLS LLP"
    assert columns[4] == "PAR"
    assert columns[6] == "HDFC0001234"
    assert columns[7] == "CORP_CLIENT_01"
    assert len(result.file_checksum_sha256) == 64


def test_ifsc_regex_validation():
    """
    Verifies that malformed IFSC codes (e.g., 5th char not '0', incorrect length) are rejected.
    """
    # 5th character '1' instead of '0'
    with pytest.raises(ValidationError):
        PayoutLineItem(
            voucher_id="v3",
            invoice_reference="INV-001",
            beneficiary_name="Vendor A",
            beneficiary_account_no="1234567890",
            beneficiary_ifsc="SBIN1001234",  # Invalid
            amount=Decimal("10000.00")
        )

    # Length 10 instead of 11
    with pytest.raises(ValidationError):
        PayoutLineItem(
            voucher_id="v4",
            invoice_reference="INV-002",
            beneficiary_name="Vendor B",
            beneficiary_account_no="1234567890",
            beneficiary_ifsc="SBIN001234",  # Invalid length
            amount=Decimal("10000.00")
        )


def test_zero_records_exception():
    """
    Verifies that attempting to generate an empty batch raises a ValueError.
    """
    with pytest.raises(ValueError):
        BankingBatchExporter.generate_icici_cib_batch(
            batch_seq=1,
            client_debit_account="167105000250",
            items=[]
        )
