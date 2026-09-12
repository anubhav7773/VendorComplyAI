-- ============================================================================
-- VENDORCOMPLY AI: CORE STATUTORY & MULTI-TENANT SCHEMA (PostgreSQL 16)
-- Migration ID: 001_initial_schema.sql
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. CUSTOM ENUMS
-- ----------------------------------------------------------------------------
CREATE TYPE public.msme_category_type AS ENUM (
    'MICRO',
    'SMALL',
    'MEDIUM',
    'UNREGISTERED'
);

CREATE TYPE public.msme_activity_type AS ENUM (
    'MANUFACTURER',
    'SERVICE_PROVIDER',
    'TRADER'
);

CREATE TYPE public.voucher_status_type AS ENUM (
    'UNPAID',
    'PARTIALLY_PAID',
    'PAID',
    'DISPUTED_HOLD'
);

CREATE TYPE public.banking_rail_type AS ENUM (
    'ICICI_CIB',
    'HDFC_ENET'
);

CREATE TYPE public.payout_status_type AS ENUM (
    'GENERATED',
    'AUTHORIZED',
    'DOWNLOADED',
    'RECONCILED',
    'CANCELLED'
);

CREATE TYPE public.objection_channel_type AS ENUM (
    'EMAIL',
    'REGISTERED_POST',
    'WHATSAPP',
    'WRITTEN_MEMO'
);

CREATE TYPE public.tenant_role_type AS ENUM (
    'PROMOTER_MD',
    'CFO',
    'ACCOUNTS_MANAGER',
    'AP_CLERK',
    'STATUTORY_AUDITOR_CA'
);

-- ----------------------------------------------------------------------------
-- 2. TABLE DEFINITIONS
-- ----------------------------------------------------------------------------

-- Table 1: Tenants
CREATE TABLE public.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_slug TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    pan VARCHAR(10) NOT NULL,
    gstin VARCHAR(15) NOT NULL,
    corporate_tax_rate NUMERIC(6, 4) NOT NULL DEFAULT 0.2517,
    tally_company_name TEXT,
    agent_secret_hash TEXT NOT NULL,
    icici_debit_account_no VARCHAR(20),
    hdfc_client_code VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_tenant_pan CHECK (pan ~ '^[A-Z]{5}[0-9]{4}[A-Z]{1}$'),
    CONSTRAINT chk_tenant_gstin CHECK (gstin ~ '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
);

-- Table 2: Tenant Users
CREATE TABLE public.tenant_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    auth_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role public.tenant_role_type NOT NULL DEFAULT 'AP_CLERK',
    can_authorize_payouts BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_tenant_auth_user UNIQUE (tenant_id, auth_user_id)
);

-- Table 3: Vendor Master
CREATE TABLE public.vendor_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    tally_ledger_name TEXT NOT NULL,
    tally_guid TEXT,
    vendor_name TEXT NOT NULL,
    pan VARCHAR(10) NOT NULL,
    gstin VARCHAR(15),
    udyam_reg_no TEXT,
    udyam_category public.msme_category_type NOT NULL DEFAULT 'UNREGISTERED',
    udyam_activity public.msme_activity_type NOT NULL DEFAULT 'MANUFACTURER',
    nic_codes TEXT[] DEFAULT '{}',
    is_trader_exempt BOOLEAN NOT NULL DEFAULT FALSE,
    default_agreed_credit_days INT NOT NULL DEFAULT 0,
    bank_name TEXT,
    bank_account_no VARCHAR(34),
    bank_ifsc VARCHAR(11),
    beneficiary_email TEXT,
    beneficiary_mobile VARCHAR(15),
    udyam_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_tenant_vendor_pan UNIQUE (tenant_id, pan),
    CONSTRAINT chk_vendor_pan CHECK (pan ~ '^[A-Z]{5}[0-9]{4}[A-Z]{1}$'),
    CONSTRAINT chk_vendor_ifsc CHECK (bank_ifsc IS NULL OR bank_ifsc ~ '^[A-Z]{4}0[A-Z0-9]{6}$')
);

-- Table 4: Purchase Vouchers
CREATE TABLE public.purchase_vouchers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES public.vendor_master(id) ON DELETE RESTRICT,
    tally_guid TEXT,
    voucher_number TEXT NOT NULL,
    invoice_reference TEXT NOT NULL,
    bill_date DATE NOT NULL,
    goods_receipt_date DATE NOT NULL,
    has_written_contract BOOLEAN NOT NULL DEFAULT FALSE,
    agreed_credit_days INT NOT NULL DEFAULT 0,
    statutory_credit_days INT NOT NULL DEFAULT 15,
    statutory_due_date DATE NOT NULL,
    taxable_amount NUMERIC(15, 2) NOT NULL,
    gst_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    total_amount NUMERIC(15, 2) NOT NULL,
    paid_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    outstanding_amount NUMERIC(15, 2) NOT NULL,
    tds_section VARCHAR(10) DEFAULT 'NONE',
    is_disputed BOOLEAN NOT NULL DEFAULT FALSE,
    status public.voucher_status_type NOT NULL DEFAULT 'UNPAID',
    raw_payload_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_tenant_invoice_ref UNIQUE (tenant_id, vendor_id, invoice_reference),
    CONSTRAINT chk_statutory_credit_cap CHECK (statutory_credit_days <= 45),
    CONSTRAINT chk_amounts_integrity CHECK (
        taxable_amount >= 0 AND
        gst_amount >= 0 AND
        total_amount >= 0 AND
        paid_amount >= 0 AND
        outstanding_amount >= 0 AND
        paid_amount <= total_amount
    )
);

-- Table 5: Voucher Payments (Waterfall Tracking)
CREATE TABLE public.voucher_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    voucher_id UUID NOT NULL REFERENCES public.purchase_vouchers(id) ON DELETE CASCADE,
    tally_payment_guid TEXT,
    payment_reference TEXT NOT NULL,
    payment_date DATE NOT NULL,
    payment_amount NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_payment_amount_positive CHECK (payment_amount > 0)
);

-- Table 6: Statutory Disputes (MSMED Sec 15 Objection Log)
CREATE TABLE public.statutory_disputes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    voucher_id UUID NOT NULL REFERENCES public.purchase_vouchers(id) ON DELETE CASCADE,
    logged_by_user_id UUID REFERENCES auth.users(id),
    objection_date DATE NOT NULL,
    objection_channel public.objection_channel_type NOT NULL,
    tracking_reference TEXT NOT NULL,
    dispute_category TEXT NOT NULL,
    dispute_details TEXT NOT NULL,
    is_settled BOOLEAN NOT NULL DEFAULT FALSE,
    settlement_date DATE,
    settlement_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_objection_date_valid CHECK (settlement_date IS NULL OR settlement_date >= objection_date)
);

-- Table 7: Statutory Exposure Cache (Materialized Rolling Computations)
CREATE TABLE public.statutory_exposure_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    voucher_id UUID NOT NULL REFERENCES public.purchase_vouchers(id) ON DELETE CASCADE,
    evaluated_as_of_date DATE NOT NULL,
    overdue_days INT NOT NULL DEFAULT 0,
    penal_interest_sec16 NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    disallowance_base_sec43bh NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    corporate_tax_exposure NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    total_statutory_exposure NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    is_43bh_applicable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_tenant_voucher_eval UNIQUE (tenant_id, voucher_id, evaluated_as_of_date)
);

-- Table 8: Batch Payout Runs
CREATE TABLE public.batch_payout_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    batch_reference VARCHAR(30) NOT NULL,
    bank_rail public.banking_rail_type NOT NULL,
    total_records INT NOT NULL,
    total_disbursement_amount NUMERIC(15, 2) NOT NULL,
    tax_disallowance_protected NUMERIC(15, 2) NOT NULL,
    penal_interest_saved NUMERIC(15, 2) NOT NULL,
    authorized_by_user_id UUID NOT NULL REFERENCES auth.users(id),
    authorized_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    file_checksum_sha256 CHAR(64) NOT NULL,
    file_storage_path TEXT,
    status public.payout_status_type NOT NULL DEFAULT 'GENERATED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_tenant_batch_reference UNIQUE (tenant_id, batch_reference)
);

-- Table 9: Batch Payout Items
CREATE TABLE public.batch_payout_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_run_id UUID NOT NULL REFERENCES public.batch_payout_runs(id) ON DELETE CASCADE,
    voucher_id UUID NOT NULL REFERENCES public.purchase_vouchers(id) ON DELETE RESTRICT,
    beneficiary_name VARCHAR(70) NOT NULL,
    beneficiary_account_no VARCHAR(34) NOT NULL,
    beneficiary_ifsc VARCHAR(11) NOT NULL,
    payout_amount NUMERIC(15, 2) NOT NULL,
    customer_reference VARCHAR(30) NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_batch_voucher UNIQUE (batch_run_id, voucher_id)
);

-- Table 10: Audit Trail (Immutable Cryptographic Log)
CREATE TABLE public.audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    actor_user_id UUID REFERENCES auth.users(id),
    action_type TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    target_entity_id UUID NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    actor_ip_address TEXT,
    actor_user_agent TEXT,
    cryptographic_signature TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 3. B-TREE COMPOSITE INDEXES
-- ----------------------------------------------------------------------------
CREATE INDEX idx_vouchers_aging_radar 
ON public.purchase_vouchers USING btree (tenant_id, statutory_due_date, status)
INCLUDE (total_amount, outstanding_amount, vendor_id);

CREATE INDEX idx_vouchers_fy_end_disallowance 
ON public.purchase_vouchers USING btree (tenant_id, bill_date, status)
INCLUDE (taxable_amount, outstanding_amount);

CREATE INDEX idx_vendor_tenant_pan 
ON public.vendor_master USING btree (tenant_id, pan);

CREATE INDEX idx_active_disputes 
ON public.statutory_disputes USING btree (tenant_id, voucher_id, is_settled);

CREATE INDEX idx_exposure_daily_eval 
ON public.statutory_exposure_cache USING btree (tenant_id, evaluated_as_of_date, total_statutory_exposure DESC);

CREATE INDEX idx_voucher_payments_order 
ON public.voucher_payments USING btree (tenant_id, voucher_id, payment_date ASC);

-- ----------------------------------------------------------------------------
-- 4. ROW-LEVEL SECURITY POLICIES & CACHED HELPER
-- ----------------------------------------------------------------------------
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vendor_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.purchase_vouchers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.voucher_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.statutory_disputes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.statutory_exposure_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.batch_payout_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.batch_payout_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_trail ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, public;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO service_role;

-- Cached security definer to fetch tenant_id from user JWT
CREATE OR REPLACE FUNCTION public.current_tenant_id()
RETURNS UUID AS $$
    SELECT NULLIF(auth.jwt() ->> 'tenant_id', '')::UUID;
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

-- Policies
CREATE POLICY "tenants_select_own" ON public.tenants
    FOR SELECT TO authenticated
    USING (id = (SELECT public.current_tenant_id()));

CREATE POLICY "tenant_users_select_same_tenant" ON public.tenant_users
    FOR SELECT TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "vendor_master_all" ON public.vendor_master
    FOR ALL TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()))
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "purchase_vouchers_all" ON public.purchase_vouchers
    FOR ALL TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()))
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "voucher_payments_all" ON public.voucher_payments
    FOR ALL TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()))
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "statutory_disputes_all" ON public.statutory_disputes
    FOR ALL TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()))
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "statutory_exposure_all" ON public.statutory_exposure_cache
    FOR ALL TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()))
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "batch_payout_runs_all" ON public.batch_payout_runs
    FOR ALL TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()))
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "batch_payout_items_all" ON public.batch_payout_items
    FOR ALL TO authenticated
    USING (batch_run_id IN (
        SELECT id FROM public.batch_payout_runs 
        WHERE tenant_id = (SELECT public.current_tenant_id())
    ));

CREATE POLICY "audit_trail_select_policy" ON public.audit_trail
    FOR SELECT TO authenticated
    USING (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "audit_trail_insert_policy" ON public.audit_trail
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = (SELECT public.current_tenant_id()));

CREATE POLICY "audit_trail_deny_update" ON public.audit_trail FOR UPDATE TO authenticated USING (FALSE);
CREATE POLICY "audit_trail_deny_delete" ON public.audit_trail FOR DELETE TO authenticated USING (FALSE);

-- ----------------------------------------------------------------------------
-- 5. AUTOMATED PL/PGSQL TRIGGERS
-- ----------------------------------------------------------------------------

-- Trigger A: updated_at synchronization
CREATE OR REPLACE FUNCTION public.set_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tenants_updated_at BEFORE UPDATE ON public.tenants FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_column();
CREATE TRIGGER trg_tenant_users_updated_at BEFORE UPDATE ON public.tenant_users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_column();
CREATE TRIGGER trg_vendor_master_updated_at BEFORE UPDATE ON public.vendor_master FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_column();
CREATE TRIGGER trg_purchase_vouchers_updated_at BEFORE UPDATE ON public.purchase_vouchers FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_column();
CREATE TRIGGER trg_batch_payout_runs_updated_at BEFORE UPDATE ON public.batch_payout_runs FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_column();
CREATE TRIGGER trg_statutory_disputes_updated_at BEFORE UPDATE ON public.statutory_disputes FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_column();

-- Trigger B: Dispute Freeze Logic (Locks Voucher & Suspends Clock)
CREATE OR REPLACE FUNCTION public.handle_statutory_dispute_insert()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.purchase_vouchers
    SET is_disputed = TRUE,
        status = 'DISPUTED_HOLD',
        updated_at = NOW()
    WHERE id = NEW.voucher_id AND tenant_id = NEW.tenant_id;

    INSERT INTO public.audit_trail (
        tenant_id,
        actor_user_id,
        action_type,
        target_entity,
        target_entity_id,
        new_state
    ) VALUES (
        NEW.tenant_id,
        NEW.logged_by_user_id,
        'DISPUTE_LOGGED_STATUTORY_HOLD',
        'purchase_vouchers',
        NEW.voucher_id,
        jsonb_build_object(
            'dispute_id', NEW.id,
            'objection_date', NEW.objection_date,
            'channel', NEW.objection_channel,
            'tracking_ref', NEW.tracking_reference,
            'category', NEW.dispute_category
        )
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_on_dispute_logged
AFTER INSERT ON public.statutory_disputes
FOR EACH ROW EXECUTE FUNCTION public.handle_statutory_dispute_insert();

-- Trigger C: Partial Payment Waterfall Reconciliation
CREATE OR REPLACE FUNCTION public.handle_voucher_payment_insert()
RETURNS TRIGGER AS $$
DECLARE
    v_total NUMERIC(15, 2);
    v_paid NUMERIC(15, 2);
    v_outstanding NUMERIC(15, 2);
    v_new_status public.voucher_status_type;
BEGIN
    SELECT total_amount INTO v_total
    FROM public.purchase_vouchers
    WHERE id = NEW.voucher_id;

    SELECT COALESCE(SUM(payment_amount), 0.00) INTO v_paid
    FROM public.voucher_payments
    WHERE voucher_id = NEW.voucher_id;

    v_outstanding := GREATEST(0.00, v_total - v_paid);

    IF v_outstanding = 0.00 THEN
        v_new_status := 'PAID';
    ELSIF v_paid > 0.00 THEN
        v_new_status := 'PARTIALLY_PAID';
    ELSE
        v_new_status := 'UNPAID';
    END IF;

    UPDATE public.purchase_vouchers
    SET paid_amount = v_paid,
        outstanding_amount = v_outstanding,
        status = v_new_status,
        updated_at = NOW()
    WHERE id = NEW.voucher_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_on_voucher_payment
AFTER INSERT OR DELETE ON public.voucher_payments
FOR EACH ROW EXECUTE FUNCTION public.handle_voucher_payment_insert();
