import json
import os
import shutil
import sys
from datetime import datetime
from collections import defaultdict

BASE_DIR       = ""
TMP_DIR = os.path.join(BASE_DIR, "tmp")
W_BYPASS_DIR   = os.path.join(BASE_DIR, "w_bypass")
DEALS_DAT      = os.path.join(TMP_DIR, "DEALS.DAT")

def parse_cob_date(date_str: str) -> str:
    dt = datetime.strptime(date_str.strip(), "%Y/%m/%d")
    return dt.strftime("%Y%m%d")


def write_deals_dat(files: list[str]) -> None:
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(DEALS_DAT, "w") as fh:
        fh.write("\n".join(files) + "\n")


def copy_deals_dat(cob_date: str) -> None:
    dest_dir = os.path.join(W_BYPASS_DIR, cob_date)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(DEALS_DAT, dest_dir)
    print(f"  ✔  Copied DEALS.DAT  →  {dest_dir}")


def group_records_by_date(records: list[dict]) -> dict:
    grouped = defaultdict(lambda: {"ritms": [], "files": [], "seen_files": set()})

    for record in records:
        cob_date = parse_cob_date(record["u_desired_completion_date"])
        entry    = grouped[cob_date]

        entry["ritms"].append(record.get("number", "N/A"))

        for f in record.get("files", []):
            if f not in entry["seen_files"]:
                entry["files"].append(f)
                entry["seen_files"].add(f)

    return {date: {"ritms": v["ritms"], "files": v["files"]}
            for date, v in grouped.items()}


def process_grouped(grouped: dict) -> None:
    for cob_date, entry in sorted(grouped.items()):
        ritms = entry["ritms"]
        files = entry["files"]

        print("=" * 60)
        print(f"  COB Date   : {cob_date}")
        print(f"  RITMs      : {', '.join(ritms)}")
        print(f"  Files ({len(files):>2}) : {', '.join(files)}")
        print("=" * 60)

        if not files:
            print("  ⚠  No files listed - skipping.\n")
            continue

        write_deals_dat(files)
        print(f"  ✔  Written DEALS.DAT  →  {DEALS_DAT}")
        copy_deals_dat(cob_date)
        print()


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <requests.json>")
        raise SystemExit(1)

    json_file = sys.argv[1]

    if not os.path.isfile(json_file):
        print(f"ERROR: File not found: {json_file}")
        raise SystemExit(1)

    with open(json_file, "r") as fh:
        data = json.load(fh)

    records = data.get("records", [])
    if not records:
        print("No records found in JSON file.")
        raise SystemExit(0)

    grouped = group_records_by_date(records)
    print(f"\nFound {len(records)} record(s) across {len(grouped)} COB date(s).\n")
    process_grouped(grouped)


if __name__ == "__main__":
    main()