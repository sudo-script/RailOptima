import argparse
import os
import sys
from typing import Tuple

from optimizer.optimizer_schedule import optimize_schedule, save_outputs
from optimizer.validate_schedule import validate_schedule as validate_opt
from Audit.Audit import run_audit


def run_pipeline(
    trains_csv: str,
    out_dir: str = "optimizer",
    audit_dir: str = "Audit",
) -> Tuple[str, str, str]:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(audit_dir, exist_ok=True)

    csv_path = os.path.join(out_dir, "schedule_output.csv")
    json_path = os.path.join(out_dir, "schedule_output.json")
    api_json_path = os.path.join(out_dir, "schedule_api.json")

    df_out = optimize_schedule(trains_csv)
    save_outputs(df_out, csv_path, json_path, api_json_path)

    val_code = validate_opt(csv_path)
    if val_code != 0:
        print("Validation reported potential conflicts.")

    audit_csv = os.path.join(audit_dir, "audit_report.csv")
    audit_xlsx = os.path.join(audit_dir, "audit_report.xlsx")
    run_audit(csv_path, audit_csv, audit_xlsx)

    return csv_path, audit_csv, api_json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run end-to-end RailOptima pipeline")
    parser.add_argument("--trains", "-t", default="trains.csv", help="Input trains CSV")
    parser.add_argument("--out-dir", default="optimizer", help="Directory for optimizer outputs")
    parser.add_argument("--audit-dir", default="Audit", help="Directory for audit outputs")
    args = parser.parse_args(argv)

    csv_path, audit_csv, api_json_path = run_pipeline(args.trains, args.out_dir, args.audit_dir)

    print("\n✅ Pipeline complete")
    print(" - Optimized schedule:", csv_path)
    print(" - Audit report:", audit_csv)
    print(" - API JSON:", api_json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
