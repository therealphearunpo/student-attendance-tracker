import csv
import importlib.util
import os
import tempfile
import unittest
from unittest.mock import patch


ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN_FILE = os.path.join(ROOT, "AttendanceRecord.py")
SPEC = importlib.util.spec_from_file_location("attendance_record", MAIN_FILE)
attendance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(attendance)


class StudentTests(unittest.TestCase):
    def test_attendance_status_updates_score(self):
        student = attendance.Student("1", "Test", "Student", "Female", "Class A", {})

        student.set_active_week(1)
        student.set_status("Present")
        student.set_active_week(2)
        student.set_status("Permission")

        self.assertEqual(student.total_score, 1.5)
        self.assertEqual(student.average_10pt, 0.9375)

    def test_cycle_status_moves_through_existing_statuses(self):
        student = attendance.Student("1", "Test", "Student", "Female", "Class A", {})

        student.cycle_status(-1)

        self.assertEqual(student.current_status_text, "Permission")


class CsvConnectionTests(unittest.TestCase):
    def test_project_student_csv_loads(self):
        path = attendance.resolve_csv_path(ROOT)
        students = attendance.load_students_from_csv(path)

        self.assertTrue(students)
        self.assertEqual(students[0].student_id, "1001")

    def test_loader_supports_excel_utf8_bom_csv(self):
        headers = attendance.CSV_COLUMNS
        row = {
            "Student ID": "7",
            "First Name": "Srey",
            "Last Name": "Chan",
            "Gender": "Female",
            "Class": "Class A",
        }
        row.update({f"Week {week}": "" for week in range(1, 17)})
        row.update({"Total (16 Max)": "0", "Average (10pt)": "0"})

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "student_record.csv")
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerow(row)

            students = attendance.load_students_from_csv(path)

        self.assertEqual(students[0].student_id, "7")
        self.assertEqual(students[0].first_name, "Srey")

    def test_loader_rejects_missing_required_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "invalid.csv")
            with open(path, "w", newline="", encoding="utf-8") as file:
                file.write("Student ID,First Name\n1,Test\n")

            with self.assertRaisesRegex(ValueError, "missing required columns"):
                attendance.load_students_from_csv(path)

    def test_save_data_writes_reloadable_csv(self):
        student = attendance.Student("9", "Test", "Student", "Female", "Class A", {})
        student.set_status("Present")

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "student_record.csv")
            app = attendance.AttendanceGUI.__new__(attendance.AttendanceGUI)
            app.students = [student]
            app.csv_filename = path

            with patch.object(attendance.messagebox, "showinfo"):
                app.save_data()

            loaded = attendance.load_students_from_csv(path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].student_id, "9")
        self.assertEqual(loaded[0].current_status_text, "Present")


if __name__ == "__main__":
    unittest.main()
