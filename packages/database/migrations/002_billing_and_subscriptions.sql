-- ============================================================================
-- VENDORCOMPLY AI: BILLING, ENTITLEMENT GATING & FINTECH RAILS SCHEMA
-- Migration ID: 002_billing_and_subscriptions.sql
-- ============================================================================

CREATE TYPE public.subscription_tier_type AS ENUM (
    'EVALUATION_TRIAL',
    'STARTER_ANNUAL',
    'GROWTH_ANNUAL',
    'ENTERPRISE_ANNUAL'
);

CREATE TYPE public.billing_status_type AS ENUM (
    'ACTIVE',
    'PAST_DUE',
    'EXPIRED',
    'TRIAL_PERIOD'
);

-- Modify tenants with billing controls
ALTER TABLE public.tenants
ADD COLUMN IF NOT EXISTS subscription_tier public.subscription_tier_type NOT NULL DEFAULT 'EVALUATION_TRIAL',
ADD COLUMN IF NOT EXISTS billing_status public.billing_status_type NOT NULL DEFAULT 'TRIAL_PERIOD',
ADD COLUMN IF NOT EXISTS subscription_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS subscription_end_date DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '30 days'),
ADD COLUMN IF NOT EXISTS monthly_bill_quota INT NOT NULL DEFAULT 50,
ADD COLUMN IF NOT EXISTS bills_processed_current_month INT NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_quota_reset_date DATE NOT NULL DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS can_export_bank_csv BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS can_access_form_3cd_pack BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS can_use_whatsapp_alerts BOOLEAN NOT NULL DEFAULT FALSE;

-- Quota reset trigger logic
CREATE OR REPLACE FUNCTION public.reset_tenant_monthly_bill_quota()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.last_quota_reset_date < CURRENT_DATE - INTERVAL '30 days' THEN
        NEW.bills_processed_current_month = 0;
        NEW.last_quota_reset_date = CURRENT_DATE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_quota_reset
BEFORE UPDATE ON public.tenants
FOR EACH ROW EXECUTE FUNCTION public.reset_tenant_monthly_bill_quota();

-- Embedded Fintech Referral Tracking (Working Capital / Bank Opening Bounties)
CREATE TABLE public.fintech_referral_leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    lead_type TEXT NOT NULL CHECK (lead_type IN ('INVOICE_FINANCING', 'BANK_ACCOUNT_OPENING')),
    requested_by_user_id UUID REFERENCES auth.users(id),
    requested_amount NUMERIC(15, 2) DEFAULT 0.00,
    target_partner TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'SUBMITTED' CHECK (status IN ('SUBMITTED', 'CONTACTED', 'DISBURSED', 'REJECTED')),
    commission_earned NUMERIC(15, 2) DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.fintech_referral_leads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "fintech_leads_tenant_isolation" ON public.fintech_referral_leads
    FOR ALL TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()))
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));
