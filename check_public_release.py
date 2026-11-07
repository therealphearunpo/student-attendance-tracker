import csv
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN_FILE = os.path.join(ROOT, 'AttendanceRecord.py')
CSV_FILE = os.path.join(ROOT, 'student_record.csv')


def print_step(title, ok, detail=''):
    status = 'OK' if ok else 'FAIL'
    print(f'[{status}] {title}')
    if detail:
        print(f'  {detail}')


def check_dependencies():
    missing = []
    for name in ['pandas', 'openpyxl']:
        try:
            __import__(name)
        except Exception:
            missing.append(name)

    try:
        import tkinter
        tkinter.Tk
    except Exception:
        missing.append('tkinter')

    ok = not missing
    detail = '' if ok else f'Missing: {", ".join(missing)}'
    print_step('Python dependencies', ok, detail)
    return ok


def check_main_file():
    if not os.path.exists(MAIN_FILE):
        print_step('Main script exists', False, MAIN_FILE)
        return False

    spec = importlib.util.spec_from_file_location('attendance_public_check', MAIN_FILE)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        has_expected = hasattr(module, 'load_students_from_csv') and hasattr(module, 'resolve_csv_path')
        if not has_expected:
            print_step('Main script imports cleanly', False, 'Expected CSV loading functions are missing')
            return False

        csv_path = module.resolve_csv_path(ROOT)
        students = module.load_students_from_csv(csv_path)
        data_ok = bool(students) and all(student.student_id for student in students)
        print_step('Main script imports cleanly', True, MAIN_FILE)
        print_step('App loads student records', data_ok, f'{len(students)} records from {os.path.basename(csv_path)}')
        return data_ok
    except Exception as exc:
        print_step('Main script imports cleanly', False, str(exc))
        return False


def check_data_file():
    if not os.path.exists(CSV_FILE):
        print_step('Student CSV file exists', False, CSV_FILE)
        return False

    try:
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
        required = {'Student ID', 'First Name', 'Last Name', 'Gender', 'Class'}
        ok = len(rows) >= 2 and required.issubset(set(rows[0]))
        print_step('Student CSV format is valid', ok, f'Rows found: {len(rows)}')
        return ok
    except Exception as exc:
        print_step('Student CSV format is valid', False, str(exc))
        return False


def main():
    print('Public release validation for the attendance project')
    print(f'Root: {ROOT}')
    checks = [
        check_dependencies(),
        check_main_file(),
        check_data_file(),
    ]
    all_ok = all(checks)
    print('')
    print_step('Overall release status', all_ok)
    if not all_ok:
        print('Install Python packages with: pip install -r requirements.txt')
        print('Tkinter must be included with your Python installation.')
        sys.exit(1)

    print('Release checks passed in this environment.')


if __name__ == '__main__':
    main()
