# apps/api/app/core/entitlements.py

from typing import Literal, Dict, Any
from fastapi import HTTPException, status


class EntitlementEnforcer:
    """
    Enforces subscription quotas and gates high-value features (Connected Banking CSV export,
    Form 3CD certified audit packages, WhatsApp OTP alerts) based on tenant tier.
    """

    @staticmethod
    def verify_bill_quota(tenant: Dict[str, Any]):
        """
        Halts invoice ingestion if the monthly quota has been exceeded.
        """
        quota = tenant.get("monthly_bill_quota", 50)
        current_count = tenant.get("bills_processed_current_month", 0)

        if current_count >= quota:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error_code": "BILL_QUOTA_EXCEEDED",
                    "message": f"Monthly invoice quota reached ({current_count}/{quota}). Upgrade to Growth Tier (₹6,500/mo) for up to 1,000 bills/month.",
                    "upgrade_url": "/settings/billing",
                },
            )

    @staticmethod
    def verify_feature_access(
        tenant: Dict[str, Any],
        feature: Literal["BANK_CSV_EXPORT", "FORM_3CD_PACK", "WHATSAPP_ALERTS"],
    ):
        """
        Enforces feature gating on API endpoints.
        """
        billing_status = tenant.get("billing_status", "TRIAL_PERIOD")

        if billing_status == "EXPIRED":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription expired. Please renew your annual plan to continue using VendorComply AI.",
            )

        if feature == "BANK_CSV_EXPORT" and not tenant.get("can_export_bank_csv", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "FEATURE_LOCKED_BANK_CSV",
                    "message": "1-Click ICICI CIB / HDFC ENet batch payment format is locked on this plan. Upgrade to the Growth Tier to unlock.",
                    "upgrade_url": "/settings/billing",
                },
            )

        if feature == "FORM_3CD_PACK" and not tenant.get("can_access_form_3cd_pack", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "FEATURE_LOCKED_3CD_PACK",
                    "message": "Certified Form 3CD Clause 22 Excel annexure pack is an exclusive Growth/Enterprise feature.",
                    "upgrade_url": "/settings/billing",
                },
            )
