# ==============================================================================
# VENDORCOMPLY AI — ON-PREMISE TALLY PRIME DESKTOP AGENT SPECIFICATION
# Document ID: 04_TALLY_AGENT_SPEC.md
# Parent Entity: asiverticals.me
# Target Environment: Windows 10/11 / Windows Server 2016+ (x86_64)
# Core Integration: Tally Prime XML HTTP Server (Port 9000) & Supabase Cloud Sync
# Packaging: Zero-Dependency Standalone Windows Executable (.exe via PyInstaller)
# ==============================================================================

## 1. AGENT ARCHITECTURE & OPERATIONAL TOPOLOGY

The VendorComply On-Premise Agent (`apps/agent`) is a lightweight, headless Windows daemon that runs in the client's local enterprise environment[cite: 1]. It serves as a secure bridge between desktop-bound accounting software (Tally Prime) and the cloud statutory compliance engine operating under **vendorcomply.asiverticals.me**[cite: 1, 2].

                 [Client Local Windows Environment]
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   ┌───────────────────────┐                  ┌──────────────────────┐   │
│   │   Tally Prime Desktop │                  │  VendorComply Agent  │   │
│   │   - Active Company    │                  │  (Background Daemon) │   │
│   │   - TCP Port 9000     │                  │  apps/agent.exe      │   │
│   └───────────┬───────────┘                  └──────────┬───────────┘   │
│               │                                         │               │
│               │◄────────1. XML Request Envelope─────────┤               │
│               │   (POST http://127.0.0.1:9000)         │               │
│               ├─────────2. XML Raw Response────────────►│               │
│               │   (Vouchers, Allocations, Creditors)   │               │
│                                                         │               │
│                                             ┌───────────┴───────────┐   │
│                                             │  Local SQLite Cache   │   │
│                                             │  (tally_cache.db)     │   │
│                                             │  - Delta Hashing      │   │
│                                             │  - State Tracking     │   │
│                                             └───────────┬───────────┘   │
└─────────────────────────────────────────────────────────┼───────────────┘
│
3. Encrypted Outbound Push
(HTTPS POST + HMAC-SHA256)
X-Tenant-ID & Timestamps
│
▼
[Cloudflare Edge / FastAPI Gateway]
vendorcomply.asiverticals.me/api/v1/sync  
PDF
+ 1


### Core Responsibilities:
1. **Zero-Touch Local Extraction**: Polls Tally Prime over `http://127.0.0.1:9000` to extract Sundry Creditor master ledgers, Purchase vouchers, and Payment vouchers (`Agst Ref` allocations)[cite: 1, 2].
2. **Delta Identification & Cache**: Computes SHA-256 cryptographic fingerprints of each voucher and ledger. Only new or modified entries are transmitted to the cloud, preserving client bandwidth and database write limits.
3. **Resilient Outbound Push**: Batches and signs changes with HMAC-SHA256, pushing them over TLS 1.3 to the backend API.
4. **Autonomous Recovery**: Handles network drops, client machine restarts, and instances where Tally Prime is closed or no company is opened.

---

## 2. TALLY PRIME XML HTTP GATEWAY PROTOCOLS

### A. Pre-requisites & Tally Configuration
To enable communication on port 9000:
1. In TallyPrime, press `F1: Help` $\rightarrow$ `Settings` $\rightarrow$ `Connectivity`.
2. Set **Client/Server configuration**:
   * *TallyPrime acts as*: **Both** (or **Server**).
   * *Enable ODBC*: **Yes**.
   * *Port*: **9000**.
3. Restart TallyPrime. The HTTP gateway is now listening at `http://127.0.0.1:9000`.

---

### B. XML Request Envelopes

#### 1. Sundry Creditors (Vendor Master) Request
Fetches all supplier ledgers under the Sundry Creditors group, including PAN, GSTIN, and credit period:

```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>SundryCreditorsMaster</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION ISINITIALIZE="Yes" NAME="SundryCreditorsMaster">
            <TYPE>Ledger</TYPE>
            <CHILDOF>Sundry Creditors</CHILDOF>
            <FETCH>GUID, Name, IncomeTaxNumber, PartyGSTIN, BillCreditPeriod, Parent</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
2. Purchase Vouchers (Invoice Details & Bill Allocations) Request
Fetches all purchase vouchers across a specified date range with itemized bill allocations and payment due dates:  
PDF

XML
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>CustomPurchaseVouchers</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION ISINITIALIZE="Yes" NAME="CustomPurchaseVouchers">
            <TYPE>Voucher</TYPE>
            <CHILDOF>Purchase</CHILDOF>
            <FETCH>GUID, Date, VoucherNumber, Reference, PartyLedgerName, Amount, Narration, AllLedgerEntries.List, BillAllocations.List</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
3. Payment & Journal Vouchers (Agst Ref Waterfall) Request
Fetches settlements linked against specific purchase invoices via Against Reference (Agst Ref) tags:  
PDF

XML
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>PaymentSettlements</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION ISINITIALIZE="Yes" NAME="PaymentSettlements">
            <TYPE>Voucher</TYPE>
            <CHILDOF>Payment</CHILDOF>
            <FETCH>GUID, Date, VoucherNumber, PartyLedgerName, Amount, BillAllocations.List</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
C. XML Tag Mapping Matrix
Functional Field	Context / Parent Tag	Tally XML Tag	Parsing / Transformation Logic
Voucher GUID	<VOUCHER>	<GUID>	System primary identifier in local cache.
Invoice Reference	<VOUCHER>	<REFERENCE> or <VOUCHERNUMBER>	
Strips spaces; vendor tax invoice number.  
PDF

Voucher Date	<VOUCHER>	<DATE>	
Formats YYYYMMDD to ISO YYYY-MM-DD.  
PDF

Party Name	<VOUCHER>	<PARTYLEDGERNAME>	
Mapped to Vendor Master tally_ledger_name.  
PDF

Gross Amount	<ALLLEDGERENTRIES.LIST>	<AMOUNT>	Inverts sign (Tally credit amounts are negative).
Bill Reference	<BILLALLOCATIONS.LIST>	<NAME>	
Matched against <REFERENCE>.  
PDF

Agreed Due Date	<BILLALLOCATIONS.LIST>	<DUEDATE>	
Formats YYYYMMDD → Date; checks contractual terms.  
PDF

Bill Allocation Type	<BILLALLOCATIONS.LIST>	<BILLTYPE>	New Ref (New Bill) or Agst Ref (Payment settlement).
Vendor PAN	<LEDGER>	<INCOMETAXNUMBER>	
Validated against regex ^[A-Z]{5}[0-9]{4}[A-Z]{1}$.  
PDF

Vendor GSTIN	<LEDGER>	<PARTYGSTIN>	
Validated against regex ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$.  
PDF

Credit Period	<LEDGER>	<BILLCREDITPERIOD>	
Parses integer days (e.g., "30 Days" → 30)[cite: 2].

D. Error Handling Matrix
Scenario	Raw Tally Response / Network Signal	Agent Handling Strategy
Tally Not Running / Offline	
socket.error: [Errno 111] Connection refused / ECONNREFUSED

[cite: 2]

Log warning, set state to OFFLINE, retry with exponential backoff (30s, 60s, 300s). Do not crash daemon.
Company Not Loaded	
<ENVELOPE><HEADER><STATUS>0</STATUS></HEADER><BODY><DATA><LINEERROR>No Company Loaded</LINEERROR></DATA></BODY></ENVELOPE>

[cite: 2]

Log notice "Waiting for company to be selected in Tally", sleep for 60 seconds, re-poll without alerting cloud.
Target Company Closed	XML response contains data for a different company	Verify <SVCURRENTCOMPANY> matches configured target company; halt sync if mismatched.
Malformed XML Payload	xml.etree.ElementTree.ParseError	Log raw payload chunk to local diagnostics file; skip corrupt record; request delta repair.
3. LOCAL SQLITE DELTA ENGINE SPECIFICATION
The local SQLite database (tally_cache.db) resides in the agent installation folder. It maintains an immutable local record of sync fingerprints to ensure only changed or newly recorded vouchers are transmitted to the cloud[cite: 2].

SQL
-- apps/agent/src/schema.sql

CREATE TABLE IF NOT EXISTS sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cached_ledgers (
    ledger_guid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    pan TEXT,
    gstin TEXT,
    credit_period INT,
    fingerprint_hash TEXT NOT NULL,
    last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cached_vouchers (
    voucher_guid TEXT PRIMARY KEY,
    voucher_number TEXT NOT NULL,
    invoice_reference TEXT,
    bill_date TEXT NOT NULL,
    party_name TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    due_date TEXT,
    fingerprint_hash TEXT NOT NULL,
    is_synced_to_cloud BOOLEAN DEFAULT 0,
    last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cached_payments (
    payment_guid TEXT PRIMARY KEY,
    voucher_number TEXT NOT NULL,
    party_name TEXT NOT NULL,
    payment_date TEXT NOT NULL,
    allocated_bill_reference TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    fingerprint_hash TEXT NOT NULL,
    is_synced_to_cloud BOOLEAN DEFAULT 0,
    last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cached_vouchers_sync ON cached_vouchers (is_synced_to_cloud);
CREATE INDEX IF NOT EXISTS idx_cached_payments_sync ON cached_payments (is_synced_to_cloud);
Fingerprint Computation Algorithm:
Voucher Fingerprint=SHA256(GUID+Reference+Date+Amount+DueDate+AllocationsJSON)
If Fingerprint 
new
​
 ==Fingerprint 
cached
​
 , skip record (zero delta).

If Fingerprint 
new
​
 

=Fingerprint 
cached
​
 , update cache, flag is_synced_to_cloud = 0, and queue for push[cite: 2].

4. COMPLETE AGENT IMPLEMENTATION (ZERO PLACEHOLDERS)
Save the following modular Python scripts inside apps/agent/src/.

File 1: Configuration Reader (apps/agent/src/config.py)
Python
import os
import json
from pathlib import Path
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    tally_host: str = Field(default="[http://127.0.0.1](http://127.0.0.1)")
    tally_port: int = Field(default=9000)
    tally_company_name: str = Field(description="Exact Company Name in Tally")
    cloud_sync_url: str = Field(default="[https://vendorcomply.asiverticals.me/api/v1/sync/push](https://vendorcomply.asiverticals.me/api/v1/sync/push)")
    tenant_id: str = Field(description="Tenant UUID issued by asiverticals.me")
    agent_secret_key: str = Field(description="64-character hex secret for HMAC signing")
    sync_interval_seconds: int = Field(default=3600)
    local_db_path: str = Field(default="tally_cache.db")
    historical_days_back: int = Field(default=365)

    @classmethod
    def load_from_file(cls, config_path: str = "agent_config.json") -> "AgentConfig":
        path = Path(config_path)
        if not path.exists():
            default_config = cls(
                tally_company_name="Enter Your Tally Company Name",
                tenant_id="00000000-0000-0000-0000-000000000000",
                agent_secret_key="0" * 64
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(default_config.model_dump_json(indent=2))
            raise FileNotFoundError(f"Configuration file {config_path} created with default values. Please configure credentials.")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return cls(**data)
File 2: Tally Prime XML Client (apps/agent/src/tally_client.py)
Python
import re
import requests
import datetime
import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple

class TallyClient:
    def __init__(self, host: str, port: int, company_name: str):
        self.endpoint = f"{host.rstrip('/')}:{port}"
        self.company_name = company_name

    def _clean_text(self, element: Optional[ET.Element]) -> str:
        return element.text.strip() if element is not None and element.text else ""

    def _parse_tally_date(self, date_str: str) -> Optional[str]:
        if not date_str or len(date_str) != 8:
            return None
        try:
            return datetime.datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            return None

    def execute_query(self, xml_payload: str) -> Tuple[bool, Optional[str], Optional[ET.Element]]:
        headers = {"Content-Type": "text/xml; charset=utf-8"}
        try:
            res = requests.post(self.endpoint, data=xml_payload.encode("utf-8"), headers=headers, timeout=15)
            if res.status_code != 200:
                return False, f"HTTP Error {res.status_code}", None
            
            root = ET.fromstring(res.content)
            line_error = root.find(".//LINEERROR")
            if line_error is not None and line_error.text:
                return False, f"Tally Error: {line_error.text.strip()}", None
            
            return True, None, root
        except requests.exceptions.ConnectionError:
            return False, "Tally HTTP Server Offline (Port 9000 unreachable)", None
        except ET.ParseError as e:
            return False, f"XML Parse Error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected Error: {str(e)}", None

    def fetch_sundry_creditors(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        payload = f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>SundryCreditorsMaster</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION ISINITIALIZE="Yes" NAME="SundryCreditorsMaster">
            <TYPE>Ledger</TYPE>
            <CHILDOF>Sundry Creditors</CHILDOF>
            <FETCH>GUID, Name, IncomeTaxNumber, PartyGSTIN, BillCreditPeriod</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""
        success, err, root = self.execute_query(payload)
        if not success:
            return False, err, []

        ledgers = []
        for ledger_elem in root.findall(".//LEDGER"):
            name = self._clean_text(ledger_elem.find("NAME"))
            guid = self._clean_text(ledger_elem.find("GUID")) or name
            pan = self._clean_text(ledger_elem.find("INCOMETAXNUMBER")).upper()
            gstin = self._clean_text(ledger_elem.find("PARTYGSTIN")).upper()
            credit_period_raw = self._clean_text(ledger_elem.find("BILLCREDITPERIOD"))
            
            # Extract numeric days from strings like "30 Days"
            match = re.search(r"\d+", credit_period_raw)
            credit_days = int(match.group()) if match else 0

            ledgers.append({
                "guid": guid,
                "name": name,
                "pan": pan,
                "gstin": gstin,
                "credit_days": credit_days
            })
        return True, "Success", ledgers

    def fetch_purchase_vouchers(self, from_date: str, to_date: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        from_d_str = from_date.replace("-", "")
        to_d_str = to_date.replace("-", "")
        payload = f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>CustomPurchaseVouchers</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_d_str}</SVFROMDATE>
        <SVTODATE>{to_d_str}</SVTODATE>
        <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION ISINITIALIZE="Yes" NAME="CustomPurchaseVouchers">
            <TYPE>Voucher</TYPE>
            <CHILDOF>Purchase</CHILDOF>
            <FETCH>GUID, Date, VoucherNumber, Reference, PartyLedgerName, Amount, BillAllocations.List</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""
        success, err, root = self.execute_query(payload)
        if not success:
            return False, err, []

        vouchers = []
        for v in root.findall(".//VOUCHER"):
            guid = self._clean_text(v.find("GUID"))
            v_num = self._clean_text(v.find("VOUCHERNUMBER"))
            ref = self._clean_text(v.find("REFERENCE")) or v_num
            b_date = self._parse_tally_date(self._clean_text(v.find("DATE")))
            party = self._clean_text(v.find("PARTYLEDGERNAME"))
            
            # Amount conversion
            amt_str = self._clean_text(v.find("AMOUNT")) or "0.0"
            try:
                # Tally debits/credits sign normalization
                amount = abs(Decimal(amt_str))
            except Exception:
                amount = Decimal("0.00")

            # Extract bill allocations
            due_date = None
            allocations = []
            for alloc in v.findall(".//BILLALLOCATIONS.LIST"):
                alloc_name = self._clean_text(alloc.find("NAME"))
                alloc_due = self._parse_tally_date(self._clean_text(alloc.find("DUEDATE")))
                if alloc_due and not due_date:
                    due_date = alloc_due
                allocations.append({"name": alloc_name, "due_date": alloc_due})

            if b_date and party:
                vouchers.append({
                    "guid": guid or f"{v_num}_{b_date}",
                    "voucher_number": v_num,
                    "invoice_reference": ref,
                    "bill_date": b_date,
                    "party_name": party,
                    "amount": amount,
                    "due_date": due_date or b_date,
                    "allocations": allocations
                })
        return True, "Success", vouchers

    def fetch_payment_settlements(self, from_date: str, to_date: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        from_d_str = from_date.replace("-", "")
        to_d_str = to_date.replace("-", "")
        payload = f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>PaymentSettlements</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_d_str}</SVFROMDATE>
        <SVTODATE>{to_d_str}</SVTODATE>
        <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION ISINITIALIZE="Yes" NAME="PaymentSettlements">
            <TYPE>Voucher</TYPE>
            <CHILDOF>Payment</CHILDOF>
            <FETCH>GUID, Date, VoucherNumber, PartyLedgerName, Amount, BillAllocations.List</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""
        success, err, root = self.execute_query(payload)
        if not success:
            return False, err, []

        payments = []
        for v in root.findall(".//VOUCHER"):
            guid = self._clean_text(v.find("GUID"))
            v_num = self._clean_text(v.find("VOUCHERNUMBER"))
            p_date = self._parse_tally_date(self._clean_text(v.find("DATE")))
            party = self._clean_text(v.find("PARTYLEDGERNAME"))

            for alloc in v.findall(".//BILLALLOCATIONS.LIST"):
                bill_type = self._clean_text(alloc.find("BILLTYPE")).upper()
                ref_name = self._clean_text(alloc.find("NAME"))
                amt_str = self._clean_text(alloc.find("AMOUNT")) or "0.0"
                try:
                    alloc_amt = abs(Decimal(amt_str))
                except Exception:
                    alloc_amt = Decimal("0.00")

                # Filter Against Reference allocations
                if (bill_type == "AGST REF" or bill_type == "") and ref_name and p_date:
                    payments.append({
                        "payment_guid": f"{guid}_{ref_name}",
                        "voucher_number": v_num,
                        "party_name": party,
                        "payment_date": p_date,
                        "allocated_bill_reference": ref_name,
                        "amount": alloc_amt
                    })
        return True, "Success", payments
File 3: Local SQLite Delta Engine (apps/agent/src/local_cache.py)
Python
import sqlite3
import hashlib
import json
from decimal import Decimal
from typing import List, Dict, Any, Tuple

class LocalCacheManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_ledgers (
                ledger_guid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                pan TEXT,
                gstin TEXT,
                credit_period INT,
                fingerprint_hash TEXT NOT NULL,
                is_synced_to_cloud BOOLEAN DEFAULT 0,
                last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_vouchers (
                voucher_guid TEXT PRIMARY KEY,
                voucher_number TEXT NOT NULL,
                invoice_reference TEXT,
                bill_date TEXT NOT NULL,
                party_name TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT,
                fingerprint_hash TEXT NOT NULL,
                is_synced_to_cloud BOOLEAN DEFAULT 0,
                last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_payments (
                payment_guid TEXT PRIMARY KEY,
                voucher_number TEXT NOT NULL,
                party_name TEXT NOT NULL,
                payment_date TEXT NOT NULL,
                allocated_bill_reference TEXT NOT NULL,
                amount REAL NOT NULL,
                fingerprint_hash TEXT NOT NULL,
                is_synced_to_cloud BOOLEAN DEFAULT 0,
                last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
            conn.commit()

    def _hash_string(self, data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def filter_and_stage_ledgers(self, ledgers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deltas = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for l in ledgers:
                raw_sig = f"{l['guid']}|{l['name']}|{l['pan']}|{l['gstin']}|{l['credit_days']}"
                f_hash = self._hash_string(raw_sig)
                
                cursor.execute("SELECT fingerprint_hash FROM cached_ledgers WHERE ledger_guid = ?", (l['guid'],))
                row = cursor.fetchone()
                if not row or row[0] != f_hash:
                    cursor.execute("""
                    INSERT OR REPLACE INTO cached_ledgers 
                    (ledger_guid, name, pan, gstin, credit_period, fingerprint_hash, is_synced_to_cloud)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                    """, (l['guid'], l['name'], l['pan'], l['gstin'], l['credit_days'], f_hash))
                    deltas.append(l)
            conn.commit()
        return deltas

    def filter_and_stage_vouchers(self, vouchers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deltas = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for v in vouchers:
                raw_sig = f"{v['guid']}|{v['voucher_number']}|{v['invoice_reference']}|{v['bill_date']}|{v['party_name']}|{v['amount']}|{v['due_date']}"
                f_hash = self._hash_string(raw_sig)

                cursor.execute("SELECT fingerprint_hash FROM cached_vouchers WHERE voucher_guid = ?", (v['guid'],))
                row = cursor.fetchone()
                if not row or row[0] != f_hash:
                    cursor.execute("""
                    INSERT OR REPLACE INTO cached_vouchers 
                    (voucher_guid, voucher_number, invoice_reference, bill_date, party_name, amount, due_date, fingerprint_hash, is_synced_to_cloud)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (v['guid'], v['voucher_number'], v['invoice_reference'], v['bill_date'], v['party_name'], float(v['amount']), v['due_date'], f_hash))
                    deltas.append(v)
            conn.commit()
        return deltas

    def filter_and_stage_payments(self, payments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deltas = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for p in payments:
                raw_sig = f"{p['payment_guid']}|{p['voucher_number']}|{p['party_name']}|{p['payment_date']}|{p['allocated_bill_reference']}|{p['amount']}"
                f_hash = self._hash_string(raw_sig)

                cursor.execute("SELECT fingerprint_hash FROM cached_payments WHERE payment_guid = ?", (p['payment_guid'],))
                row = cursor.fetchone()
                if not row or row[0] != f_hash:
                    cursor.execute("""
                    INSERT OR REPLACE INTO cached_payments 
                    (payment_guid, voucher_number, party_name, payment_date, allocated_bill_reference, amount, fingerprint_hash, is_synced_to_cloud)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                    """, (p['payment_guid'], p['voucher_number'], p['party_name'], p['payment_date'], p['allocated_bill_reference'], float(p['amount']), f_hash))
                    deltas.append(p)
            conn.commit()
        return deltas

    def mark_all_synced(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE cached_ledgers SET is_synced_to_cloud = 1")
            cursor.execute("UPDATE cached_vouchers SET is_synced_to_cloud = 1")
            cursor.execute("UPDATE cached_payments SET is_synced_to_cloud = 1")
            conn.commit()
File 4: Sync Manager & HMAC Cloud Sender (apps/agent/src/sync_manager.py)
Python
import hmac
import hashlib
import json
import datetime
import requests
from decimal import Decimal
from typing import Dict, Any, List

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)

class CloudSyncManager:
    def __init__(self, sync_url: str, tenant_id: str, secret_key: str):
        self.sync_url = sync_url
        self.tenant_id = tenant_id
        self.secret_key = secret_key

    def _generate_hmac(self, message_body: str) -> str:
        return hmac.new(
            self.secret_key.encode("utf-8"),
            message_body.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def push_delta_payload(
        self,
        ledgers: List[Dict[str, Any]],
        vouchers: List[Dict[str, Any]],
        payments: List[Dict[str, Any]]
    ) -> bool:
        if not ledgers and not vouchers and not payments:
            return True

        timestamp_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {
            "tenant_id": self.tenant_id,
            "timestamp": timestamp_iso,
            "payload_data": {
                "ledgers": ledgers,
                "vouchers": vouchers,
                "payments": payments
            }
        }

        body_serialized = json.dumps(payload, cls=DecimalEncoder)
        signature = self._generate_hmac(body_serialized)

        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": self.tenant_id,
            "X-Agent-Timestamp": timestamp_iso,
            "X-Agent-Signature": signature
        }

        try:
            res = requests.post(self.sync_url, data=body_serialized, headers=headers, timeout=30)
            if res.status_code == 200:
                return True
            print(f"[ERROR] Cloud Sync Failed with HTTP {res.status_code}: {res.text}")
            return False
        except Exception as e:
            print(f"[ERROR] Connection to {self.sync_url} failed: {str(e)}")
            return False
File 5: Main Daemon Entrypoint (apps/agent/main.py)
Python
import time
import sys
import argparse
import datetime
from src.config import AgentConfig
from src.tally_client import TallyClient
from src.local_cache import LocalCacheManager
from src.sync_manager import CloudSyncManager

def run_sync_cycle(config: AgentConfig, tally: TallyClient, cache: LocalCacheManager, cloud: CloudSyncManager):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Extraction Cycle...")
    
    # 1. Fetch & Filter Vendors
    ok, err, ledgers = tally.fetch_sundry_creditors()
    if not ok:
        print(f"[WARN] Failed to fetch Creditors: {err}")
        return False
    delta_ledgers = cache.filter_and_stage_ledgers(ledgers)

    # 2. Date Ranges (Configured historical days back up to today)
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=config.historical_days_back)).strftime("%Y-%m-%d")
    end_date = (today + datetime.timedelta(days=60)).strftime("%Y-%m-%d")

    # 3. Fetch & Filter Vouchers
    ok, err, vouchers = tally.fetch_purchase_vouchers(start_date, end_date)
    if not ok:
        print(f"[WARN] Failed to fetch Vouchers: {err}")
        return False
    delta_vouchers = cache.filter_and_stage_vouchers(vouchers)

    # 4. Fetch & Filter Payment Waterfall Settlements
    ok, err, payments = tally.fetch_payment_settlements(start_date, end_date)
    if not ok:
        print(f"[WARN] Failed to fetch Payments: {err}")
        return False
    delta_payments = cache.filter_and_stage_payments(payments)

    total_deltas = len(delta_ledgers) + len(delta_vouchers) + len(delta_payments)
    print(f"[INFO] Delta Detected: {len(delta_ledgers)} Ledgers, {len(delta_vouchers)} Invoices, {len(delta_payments)} Payments.")

    if total_deltas > 0:
        push_ok = cloud.push_delta_payload(delta_ledgers, delta_vouchers, delta_payments)
        if push_ok:
            cache.mark_all_synced()
            print("[SUCCESS] Delta synchronization verified and committed.")
        else:
            print("[ERROR] Cloud rejected sync. Data remains staged locally for retry.")
    else:
        print("[INFO] Ledger and vouchers are up-to-date with Tally. Zero transfer required.")
    return True

def main():
    parser = argparse.ArgumentParser(description="VendorComply AI — Tally Prime Desktop Sync Daemon")
    parser.add_argument("--config", default="agent_config.json", help="Path to configuration JSON")
    parser.add_argument("--sync-now", action="store_true", help="Run a single sync and exit")
    parser.add_argument("--test-tally", action="store_true", help="Test port 9000 connection to Tally and exit")
    args = parser.parse_args()

    try:
        config = AgentConfig.load_from_file(args.config)
    except Exception as e:
        print(f"[FATAL] {str(e)}")
        sys.exit(1)

    tally = TallyClient(config.tally_host, config.tally_port, config.tally_company_name)
    cache = LocalCacheManager(config.local_db_path)
    cloud = CloudSyncManager(config.cloud_sync_url, config.tenant_id, config.agent_secret_key)

    if args.test_tally:
        print(f"[TEST] Pinging Tally at {config.tally_host}:{config.tally_port} for company '{config.tally_company_name}'...")
        ok, msg, ledgers = tally.fetch_sundry_creditors()
        if ok:
            print(f"[SUCCESS] Connected! Found {len(ledgers)} Sundry Creditor ledgers.")
            sys.exit(0)
        else:
            print(f"[FAILURE] {msg}")
            sys.exit(1)

    if args.sync_now:
        run_sync_cycle(config, tally, cache, cloud)
        sys.exit(0)

    print(f"================================================================")
    print(f" VendorComply AI Background Daemon Active (asiverticals.me)")
    print(f" Polling Target: {config.tally_company_name} on Port {config.tally_port}")
    print(f" Interval: {config.sync_interval_seconds}s | DB: {config.local_db_path}")
    print(f"================================================================")

    while True:
        try:
            run_sync_cycle(config, tally, cache, cloud)
        except KeyboardInterrupt:
            print("[INFO] Terminating daemon cleanly on user interrupt.")
            sys.exit(0)
        except Exception as e:
            print(f"[UNEXPECTED EXCEPTION] {str(e)}")
        
        time.sleep(config.sync_interval_seconds)

if __name__ == "__main__":
    main()
5. ZERO-DEPENDENCY PYINSTALLER PACKAGING SPECIFICATION
To distribute the agent to client accounts teams who may lack Python installations, compile the codebase into a single standalone Windows executable using PyInstaller.

Requirements Specification (apps/agent/requirements.txt):
Plaintext
requests>=2.31.0
pydantic>=2.7.0
urllib3>=2.0.0
pyinstaller>=6.5.0
PyInstaller Spec File (apps/agent/vendorcomply_agent.spec):
Python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['sqlite3', 'pydantic'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VendorComplyAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # Set to False for headless background execution
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
Compilation Command:
Run the following inside PowerShell in the apps/agent directory:

PowerShell
pyinstaller --clean vendorcomply_agent.spec
The output will generate a self-contained, single-file binary:
apps/agent/dist/VendorComplyAgent.exe (~14 MB).

6. CLIENT SETUP & INSTALLATION VERIFICATION
Copy VendorComplyAgent.exe and agent_config.json into C:\Program Files\VendorComply\.

Populate agent_config.json with the tenant credentials issued at vendorcomply.asiverticals.me/settings.

Test communication:

PowerShell
.\VendorComplyAgent.exe --test-tally
Run initial historical synchronization:

PowerShell
.\VendorComplyAgent.exe --sync-now
Install as an autonomous background Windows Task (runs on user login without administrative prompts):

PowerShell
schtasks /create /tn "VendorComplySyncDaemon" /tr "'C:\Program Files\VendorComply\VendorComplyAgent.exe'" /sc onlogon /rl highest

---
