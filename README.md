# Student Attendance Tracker

A desktop student attendance tracker built with Python, Tkinter, and CSV files.
The app records weekly attendance as Present, Permission, Late, or Absent.

Copyright (c) 2026 Po Phearun. All rights reserved. See [COPYRIGHT](./COPYRIGHT).

## Requirements

- Python 3.9 or later
- Tkinter (included with most Windows Python installations)
- Packages listed in `requirements.txt`

Install the Python packages:

```powershell
python -m pip install -r requirements.txt
```

## Run

Keep `AttendanceRecord.py` and `student_record.csv` in the same folder, then run:

```powershell
python AttendanceRecord.py
```

The app reads and saves attendance in `student_record.csv`. Keep a backup before
editing or replacing the student data file.

## Convert an Excel student list

The workbook must contain the columns `Student ID`, `First Name`, `Last Name`,
`Gender`, and `Class`. Convert to a new CSV (or choose another output path):

```powershell
python convert_to_csv.py --input student_record.xlsx --output imported_students.csv
```

To deliberately replace an existing CSV, include `--overwrite`.

## Check and test

Run the release checks and tests:

```powershell
python check_public_release.py
python -m unittest test_attendance.py
```
