# apps/api/tests/test_entitlements.py

import pytest
from fastapi import HTTPException
from app.core.entitlements import EntitlementEnforcer


def test_verify_bill_quota_within_limit():
    tenant = {
        "monthly_bill_quota": 100,
        "bills_processed_current_month": 50,
    }
    # Should not raise
    EntitlementEnforcer.verify_bill_quota(tenant)


def test_verify_bill_quota_exceeded():
    tenant = {
        "monthly_bill_quota": 50,
        "bills_processed_current_month": 50,
    }
    with pytest.raises(HTTPException) as exc_info:
        EntitlementEnforcer.verify_bill_quota(tenant)
    assert exc_info.value.status_code == 402
    assert exc_info.value.detail["error_code"] == "BILL_QUOTA_EXCEEDED"


def test_verify_feature_access_expired():
    tenant = {
        "billing_status": "EXPIRED",
        "can_export_bank_csv": True,
    }
    with pytest.raises(HTTPException) as exc_info:
        EntitlementEnforcer.verify_feature_access(tenant, "BANK_CSV_EXPORT")
    assert exc_info.value.status_code == 402


def test_verify_feature_access_locked():
    tenant = {
        "billing_status": "ACTIVE",
        "can_export_bank_csv": False,
        "can_access_form_3cd_pack": False,
    }
    with pytest.raises(HTTPException) as exc_info:
        EntitlementEnforcer.verify_feature_access(tenant, "BANK_CSV_EXPORT")
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["error_code"] == "FEATURE_LOCKED_BANK_CSV"

    with pytest.raises(HTTPException) as exc_info2:
        EntitlementEnforcer.verify_feature_access(tenant, "FORM_3CD_PACK")
    assert exc_info2.value.status_code == 403
    assert exc_info2.value.detail["error_code"] == "FEATURE_LOCKED_3CD_PACK"


def test_verify_feature_access_granted():
    tenant = {
        "billing_status": "ACTIVE",
        "can_export_bank_csv": True,
        "can_access_form_3cd_pack": True,
    }
    # Should not raise
    EntitlementEnforcer.verify_feature_access(tenant, "BANK_CSV_EXPORT")
    EntitlementEnforcer.verify_feature_access(tenant, "FORM_3CD_PACK")
