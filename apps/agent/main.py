# apps/agent/main.py

import time
import sys
import argparse
import datetime
from src.config import AgentConfig
from src.tally_client import TallyClient
from src.local_cache import LocalCacheManager
from src.sync_manager import CloudSyncManager


def run_sync_cycle(config: AgentConfig, tally: TallyClient, cache: LocalCacheManager, cloud: CloudSyncManager):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Polling Tally Prime...")

    # 1. Fetch Vendors
    ok, err, ledgers = tally.fetch_sundry_creditors()
    if not ok:
        print(f"[WARN] Failed to fetch Creditors: {err}")
        return False
    delta_ledgers = cache.filter_and_stage_ledgers(ledgers)

    # 2. Date Ranges
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=config.historical_days_back)).strftime("%Y-%m-%d")
    end_date = (today + datetime.timedelta(days=60)).strftime("%Y-%m-%d")

    # 3. Fetch Vouchers
    ok, err, vouchers = tally.fetch_purchase_vouchers(start_date, end_date)
    if not ok:
        print(f"[WARN] Failed to fetch Vouchers: {err}")
        return False
    delta_vouchers = cache.filter_and_stage_vouchers(vouchers)

    # 4. Fetch Payments Waterfall
    ok, err, payments = tally.fetch_payment_settlements(start_date, end_date)
    if not ok:
        print(f"[WARN] Failed to fetch Payments: {err}")
        return False
    delta_payments = cache.filter_and_stage_payments(payments)

    total_deltas = len(delta_ledgers) + len(delta_vouchers) + len(delta_payments)
    print(f"[INFO] Deltas Detected: {len(delta_ledgers)} Ledgers, {len(delta_vouchers)} Invoices, {len(delta_payments)} Payments.")

    if total_deltas > 0:
        push_ok = cloud.push_delta_payload(delta_ledgers, delta_vouchers, delta_payments)
        if push_ok:
            cache.mark_all_synced()
            print("[SUCCESS] Delta synchronization verified and committed to cloud.")
        else:
            print("[ERROR] Cloud rejected payload. Data remains staged locally for retry.")
    else:
        print("[INFO] Everything is up-to-date with Tally. Zero transfer required.")
    return True


def main():
    parser = argparse.ArgumentParser(description="VendorComply AI — Tally Prime Desktop Sync Daemon")
    parser.add_argument("--config", default="agent_config.json", help="Path to agent configuration JSON")
    parser.add_argument("--sync-now", action="store_true", help="Run a single sync cycle and exit")
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
        print(f"[TEST] Testing Tally connection at {config.tally_host}:{config.tally_port} for company '{config.tally_company_name}'...")
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

    print("================================================================")
    print(" VendorComply AI Background Daemon Active (asiverticals.me)")
    print(f" Target: {config.tally_company_name} on Port {config.tally_port}")
    print("================================================================")

    while True:
        try:
            run_sync_cycle(config, tally, cache, cloud)
        except KeyboardInterrupt:
            print("[INFO] Terminating daemon cleanly.")
            sys.exit(0)
        except Exception as e:
            print(f"[UNEXPECTED EXCEPTION] {str(e)}")

        time.sleep(config.sync_interval_seconds)


if __name__ == "__main__":
    main()
