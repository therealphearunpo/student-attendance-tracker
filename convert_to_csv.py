import argparse
import os

import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIRED_COLUMNS = {"Student ID", "First Name", "Last Name", "Gender", "Class"}
EXCEL_FILES = ("student_record.xlsx", "ITE-G11-Y3S1.xlsx", "ITE_Y3A2_S1_Schedule.xlsx")
CSV_FILES = ("student_record.csv", "ITE_Y3A2_S1_Schedule.csv", "ITE_Y3A2_Students.csv")


def first_existing(names):
    for name in names:
        path = os.path.join(BASE_DIR, name)
        if os.path.isfile(path):
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description="Convert a student Excel workbook to CSV.")
    parser.add_argument("--input", help="Excel workbook path (default: first supported project workbook)")
    parser.add_argument("--output", help="CSV output path (default: first supported project CSV)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing CSV file",
    )
    args = parser.parse_args()

    excel_file = os.path.abspath(args.input) if args.input else first_existing(EXCEL_FILES)
    if not excel_file or not os.path.isfile(excel_file):
        print("Error: No Excel file found. Use --input to specify a workbook.")
        return 1

    existing_csv = first_existing(CSV_FILES)
    csv_file = os.path.abspath(args.output) if args.output else (
        existing_csv or os.path.join(BASE_DIR, "student_record.csv")
    )
    if os.path.exists(csv_file) and not args.overwrite:
        print(f"Refusing to overwrite existing data file: {csv_file}")
        print("Use --output to choose another file or --overwrite to replace it.")
        return 1

    try:
        print(f"Reading '{excel_file}'...")
        df = pd.read_excel(excel_file)
        missing_columns = REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Workbook is missing required student columns: {missing}")

        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"Success! Converted to '{csv_file}'")
        return 0
    except (OSError, ImportError, ValueError) as error:
        print(f"Conversion failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
