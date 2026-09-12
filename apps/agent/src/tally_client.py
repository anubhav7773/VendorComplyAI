# apps/agent/src/tally_client.py

import re
import datetime
import requests
import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple


class TallyClient:
    """
    Interfaces directly with Tally Prime's local XML HTTP Server on port 9000.
    Builds raw TDL XML export envelopes and parses responses.
    """

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

    def execute_xml_request(self, xml_payload: str) -> Tuple[bool, Optional[str], Optional[ET.Element]]:
        headers = {"Content-Type": "text/xml; charset=utf-8"}
        try:
            res = requests.post(self.endpoint, data=xml_payload.encode("utf-8"), headers=headers, timeout=15)
            if res.status_code != 200:
                return False, f"HTTP Error {res.status_code}", None

            root = ET.fromstring(res.content)
            # Scenario A: Company not loaded error envelope
            line_error = root.find(".//LINEERROR")
            if line_error is not None and line_error.text:
                return False, f"Tally Prime Error: {line_error.text.strip()}", None

            return True, None, root
        except requests.exceptions.ConnectionError:
            # Scenario B: Tally HTTP Server Offline / Port 9000 ECONNREFUSED
            return False, "Tally HTTP Server Offline (Port 9000 ECONNREFUSED)", None
        except ET.ParseError as e:
            return False, f"XML Parse Error: {str(e)}", None
        except Exception as e:
            return False, f"Transport Error: {str(e)}", None

    def fetch_sundry_creditors(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Fetches vendor master data under Sundry Creditors along with PAN, GSTIN, and Credit Period.
        """
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
<COLLECTION NAME="SundryCreditorsMaster" ISINITIALIZE="Yes">
<TYPE>Ledger</TYPE>
<CHILDOF>Sundry Creditors</CHILDOF>
<FETCH>Name, IncomeTaxNumber, PartyGSTIN, BillCreditPeriod, Parent</FETCH>
</COLLECTION>
</TDLMESSAGE>
</TDL>
</DESC>
</BODY>
</ENVELOPE>"""
        success, err, root = self.execute_xml_request(payload)
        if not success or root is None:
            return False, err or "Unknown Error", []

        ledgers = []
        for ledger_elem in root.findall(".//LEDGER"):
            name = self._clean_text(ledger_elem.find("NAME"))
            pan = self._clean_text(ledger_elem.find("INCOMETAXNUMBER")).upper()
            gstin = self._clean_text(ledger_elem.find("PARTYGSTIN")).upper()
            credit_period_raw = self._clean_text(ledger_elem.find("BILLCREDITPERIOD"))

            match = re.search(r"\d+", credit_period_raw)
            credit_days = int(match.group()) if match else 0

            if name:
                ledgers.append({
                    "name": name,
                    "pan": pan,
                    "gstin": gstin,
                    "credit_days": credit_days
                })
        return True, "Success", ledgers

    def fetch_purchase_vouchers(self, from_date: str, to_date: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Fetches Purchase Vouchers between date range with BillAllocations.
        """
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
<COLLECTION NAME="CustomPurchaseVouchers" ISINITIALIZE="Yes">
<TYPE>Voucher</TYPE>
<CHILDOF>Purchase</CHILDOF>
<FETCH>Date, VoucherNumber, Reference, PartyLedgerName, Amount, AllLedgerEntries.List, BillAllocations.List</FETCH>
</COLLECTION>
</TDLMESSAGE>
</TDL>
</DESC>
</BODY>
</ENVELOPE>"""
        success, err, root = self.execute_xml_request(payload)
        if not success or root is None:
            return False, err or "Unknown Error", []

        vouchers = []
        for v in root.findall(".//VOUCHER"):
            v_num = self._clean_text(v.find("VOUCHERNUMBER"))
            ref = self._clean_text(v.find("REFERENCE")) or v_num
            b_date = self._parse_tally_date(self._clean_text(v.find("DATE")))
            party = self._clean_text(v.find("PARTYLEDGERNAME"))

            amt_str = self._clean_text(v.find("AMOUNT")) or "0.0"
            try:
                # Tally balances sign inversion
                amount = abs(Decimal(amt_str))
            except Exception:
                amount = Decimal("0.00")

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
        """
        Fetches Payment vouchers with Against Reference ('Agst Ref') bill allocations.
        """
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
<COLLECTION NAME="PaymentSettlements" ISINITIALIZE="Yes">
<TYPE>Voucher</TYPE>
<CHILDOF>Payment</CHILDOF>
<FETCH>Date, VoucherNumber, PartyLedgerName, Amount, BillAllocations.List</FETCH>
</COLLECTION>
</TDLMESSAGE>
</TDL>
</DESC>
</BODY>
</ENVELOPE>"""
        success, err, root = self.execute_xml_request(payload)
        if not success or root is None:
            return False, err or "Unknown Error", []

        payments = []
        for v in root.findall(".//VOUCHER"):
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
                if (bill_type in ["AGST REF", ""]) and ref_name and p_date:
                    payments.append({
                        "payment_reference": f"{v_num}_{ref_name}",
                        "voucher_number": v_num,
                        "party_name": party,
                        "payment_date": p_date,
                        "allocated_bill_reference": ref_name,
                        "amount": alloc_amt
                    })
        return True, "Success", payments
