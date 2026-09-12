# apps/agent/src/local_cache.py

import sqlite3
import hashlib
from typing import List, Dict, Any


class LocalCacheManager:
    """
    Maintains local SQLite cache of ledger and voucher SHA-256 fingerprints.
    Ensures zero cloud bandwidth waste by staging strictly modified/new deltas.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._mem_conn = sqlite3.connect(":memory:") if db_path == ":memory:" else None
        self._init_db()

    def _get_connection(self):
        if self._mem_conn is not None:
            return self._mem_conn
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_ledgers (
                name TEXT PRIMARY KEY,
                pan TEXT,
                gstin TEXT,
                credit_period INT,
                fingerprint_hash TEXT NOT NULL,
                is_synced_to_cloud BOOLEAN DEFAULT 0,
                last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_vouchers (
                voucher_key TEXT PRIMARY KEY,
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
                payment_ref TEXT PRIMARY KEY,
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

    @staticmethod
    def _hash_string(data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def filter_and_stage_ledgers(self, ledgers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deltas = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for l in ledgers:
                raw_sig = f"{l['name']}|{l['pan']}|{l['gstin']}|{l['credit_days']}"
                f_hash = self._hash_string(raw_sig)

                cursor.execute("SELECT fingerprint_hash FROM cached_ledgers WHERE name = ?", (l['name'],))
                row = cursor.fetchone()
                if not row or row[0] != f_hash:
                    cursor.execute("""
                    INSERT OR REPLACE INTO cached_ledgers 
                    (name, pan, gstin, credit_period, fingerprint_hash, is_synced_to_cloud)
                    VALUES (?, ?, ?, ?, ?, 0)
                    """, (l['name'], l['pan'], l['gstin'], l['credit_days'], f_hash))
                    deltas.append(l)
            conn.commit()
        return deltas

    def filter_and_stage_vouchers(self, vouchers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deltas = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for v in vouchers:
                v_key = f"{v['party_name']}_{v['invoice_reference']}_{v['bill_date']}"
                raw_sig = f"{v_key}|{v['voucher_number']}|{v['amount']}|{v['due_date']}"
                f_hash = self._hash_string(raw_sig)

                cursor.execute("SELECT fingerprint_hash FROM cached_vouchers WHERE voucher_key = ?", (v_key,))
                row = cursor.fetchone()
                if not row or row[0] != f_hash:
                    cursor.execute("""
                    INSERT OR REPLACE INTO cached_vouchers 
                    (voucher_key, voucher_number, invoice_reference, bill_date, party_name, amount, due_date, fingerprint_hash, is_synced_to_cloud)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (v_key, v['voucher_number'], v['invoice_reference'], v['bill_date'], v['party_name'], float(v['amount']), v['due_date'], f_hash))
                    deltas.append(v)
            conn.commit()
        return deltas

    def filter_and_stage_payments(self, payments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deltas = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for p in payments:
                p_ref = p['payment_reference']
                raw_sig = f"{p_ref}|{p['voucher_number']}|{p['party_name']}|{p['payment_date']}|{p['allocated_bill_reference']}|{p['amount']}"
                f_hash = self._hash_string(raw_sig)

                cursor.execute("SELECT fingerprint_hash FROM cached_payments WHERE payment_ref = ?", (p_ref,))
                row = cursor.fetchone()
                if not row or row[0] != f_hash:
                    cursor.execute("""
                    INSERT OR REPLACE INTO cached_payments 
                    (payment_ref, voucher_number, party_name, payment_date, allocated_bill_reference, amount, fingerprint_hash, is_synced_to_cloud)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                    """, (p_ref, p['voucher_number'], p['party_name'], p['payment_date'], p['allocated_bill_reference'], float(p['amount']), f_hash))
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
