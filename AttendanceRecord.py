import os
import csv
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox

CSV_COLUMNS = [
    "Student ID",
    "First Name",
    "Last Name",
    "Gender",
    "Class",
    *[f"Week {i}" for i in range(1, 17)],
    "Total (16 Max)",
    "Average (10pt)",
]
REQUIRED_CSV_COLUMNS = CSV_COLUMNS[:5]

class Student:
    STATUS_MAP = {"Present": 1.0, "Permission": 0.5, "Late": 0.75, "Absent": 0.0}
    VAL_MAP = {1.0: "Present", 0.5: "Permission", 0.75: "Late", 0.0: "Absent"}
    STATUSES = ["Present", "Permission", "Absent", "Late"]

    def __init__(self, student_id: str, first_name: str, last_name: str, gender: str, your_class: str, weeks_data: dict):
        self.student_id = str(student_id)
        self.first_name = str(first_name)
        self.last_name = str(last_name)
        self.gender = str(gender)
        self.your_class = str(your_class)
        self.weeks = weeks_data
        self.active_week = "Week 1"
        
    def set_active_week(self, week_num: int):
        self.active_week = f"Week {week_num}"
        
    @property
    def display_name(self) -> str:
        return f"{self.first_name.title()} {self.last_name.title()}"

    @property
    def current_status_text(self) -> str:
        val = self.weeks.get(self.active_week, "0.0")
        if not val: val = "0.0"
        try:
            val = float(val)
        except:
            val = 0.0
        return self.VAL_MAP.get(val, "Absent")

    def set_status(self, status_text: str):
        if status_text in self.STATUS_MAP:
            self.weeks[self.active_week] = self.STATUS_MAP[status_text]

    def cycle_status(self, direction: int):
        current_idx = self.STATUSES.index(self.current_status_text)
        new_idx = (current_idx + direction) % len(self.STATUSES)
        self.set_status(self.STATUSES[new_idx])

    @property
    def total_score(self) -> float:
        total = 0.0
        for i in range(1, 17):
            val = self.weeks.get(f"Week {i}", 0.0)
            if val != "" and val is not None:
                try:
                    total += float(val)
                except ValueError:
                    pass
        return total

    @property
    def average_10pt(self) -> float:
        return (self.total_score / 16.0) * 10.0

    def to_dict(self) -> dict:
        row = {
            "Student ID": self.student_id,
            "First Name": self.first_name,
            "Last Name": self.last_name,
            "Gender": self.gender,
            "Class": self.your_class,
        }
        for i in range(1, 17):
            week_key = f"Week {i}"
            row[week_key] = self.weeks.get(week_key, "")
        row["Total (16 Max)"] = round(self.total_score, 2)
        row["Average (10pt)"] = round(self.average_10pt, 2)
        return row

# ==========================================
# 3. CSV File Handlers
# ==========================================
def load_students_from_csv(filename: str) -> list:
    students = []
    if not os.path.exists(filename):
        return students
    with open(filename, mode='r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        missing_columns = set(REQUIRED_CSV_COLUMNS) - set(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV file is missing required columns: {missing}")
        for row in reader:
            if not str(row.get("Student ID") or "").strip():
                continue
            weeks_data = {}
            for i in range(1, 17):
                weeks_data[f"Week {i}"] = row.get(f"Week {i}", "")
            student = Student(
                student_id=row.get("Student ID", "N/A"),
                first_name=row.get("First Name", "N/A"),
                last_name=row.get("Last Name", ""),
                gender=row.get("Gender", ""),
                your_class=row.get("Class", "N/A"),
                weeks_data=weeks_data
            )
            students.append(student)
    return students

# ==========================================
# 4. GUI Application (Tkinter)
# ==========================================
class AttendanceGUI:
    def __init__(self, root, students, csv_filename):
        self.root = root
        self.students = students
        self.csv_filename = csv_filename
        self.current_week = 1
        
        self.root.title("Student Attendance Tracker - ITE")
        self.root.geometry("900x600")
        
        self.setup_ui()
        self.load_week_data()

    def setup_ui(self):
        # Top Frame
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="Select Week:", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.week_var = tk.IntVar(value=1)
        self.week_spinbox = ttk.Spinbox(top_frame, from_=1, to=16, textvariable=self.week_var, width=5, font=("Arial", 12), command=self.load_week_data)
        self.week_spinbox.pack(side=tk.LEFT)
        
        # Table Frame (Treeview)
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "name", "gender", "status", "total", "score")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("gender", text="Gender")
        self.tree.heading("status", text="Status")
        self.tree.heading("total", text="Total (16)")
        self.tree.heading("score", text="Score (10pt)")

        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("gender", width=80, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("total", width=80, anchor=tk.CENTER)
        self.tree.column("score", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.root.bind("<Left>", lambda e: self.change_status_keyboard(-1))
        self.root.bind("<Right>", lambda e: self.change_status_keyboard(1))
        
        # Bottom Controls
        bottom_frame = tk.Frame(self.root, pady=10)
        bottom_frame.pack(fill=tk.X)

        btn_present = tk.Button(bottom_frame, text="Present", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), command=lambda: self.set_status_for_selected("Present"))
        btn_present.pack(side=tk.LEFT, padx=10)

        btn_perm = tk.Button(bottom_frame, text="Permission", bg="#FF9800", fg="white", font=("Arial", 11, "bold"), command=lambda: self.set_status_for_selected("Permission"))
        btn_perm.pack(side=tk.LEFT, padx=10)

        btn_absent = tk.Button(bottom_frame, text="Absent", bg="#F44336", fg="white", font=("Arial", 11, "bold"), command=lambda: self.set_status_for_selected("Absent"))
        btn_absent.pack(side=tk.LEFT, padx=10)
        
        btn_late = tk.Button(bottom_frame, text="Late", bg="#9C27B0", fg="white", font=("Arial", 11, "bold"), command=lambda: self.set_status_for_selected("Late"))
        btn_late.pack(side=tk.LEFT, padx=10)

        btn_save = tk.Button(bottom_frame, text="💾 Save to CSV", bg="#2196F3", fg="white", font=("Arial", 11, "bold"), command=self.save_data)
        btn_save.pack(side=tk.RIGHT, padx=20)

    def load_week_data(self):
        self.current_week = self.week_var.get()
        for student in self.students:
            student.set_active_week(self.current_week)
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for idx, student in enumerate(self.students):
            self.tree.insert("", tk.END, iid=str(idx), values=(
                student.student_id,
                student.display_name,
                student.gender,
                student.current_status_text,
                f"{student.total_score:g}",
                f"{student.average_10pt:.2f}"
            ))

    def update_row(self, idx):
        student = self.students[idx]
        self.tree.item(str(idx), values=(
            student.student_id,
            student.display_name,
            student.gender,
            student.current_status_text,
            f"{student.total_score:g}",
            f"{student.average_10pt:.2f}"
        ))

    def set_status_for_selected(self, status):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        self.students[idx].set_status(status)
        self.update_row(idx)
        self.move_selection_down()

    def change_status_keyboard(self, direction):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        self.students[idx].cycle_status(direction)
        self.update_row(idx)

    def move_selection_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        if idx < len(self.students) - 1:
            next_idx = str(idx + 1)
            self.tree.selection_set(next_idx)
            self.tree.focus(next_idx)
            self.tree.see(next_idx)

    def save_data(self):
        temporary_file = None
        try:
            data_dicts = [student.to_dict() for student in self.students]
            output_dir = os.path.dirname(os.path.abspath(self.csv_filename))
            with tempfile.NamedTemporaryFile(
                mode='w',
                newline='',
                encoding='utf-8-sig',
                dir=output_dir,
                prefix=".attendance-",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_file = file.name
                writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerows(data_dicts)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_file, self.csv_filename)
            temporary_file = None
            messagebox.showinfo("Success", f"Attendance data saved successfully to:\n{self.csv_filename}")
        except Exception as e:
            if temporary_file and os.path.exists(temporary_file):
                try:
                    os.remove(temporary_file)
                except OSError as cleanup_error:
                    e = OSError(f"{e}. Could not remove temporary file {temporary_file}: {cleanup_error}")
            messagebox.showerror("Error", f"Could not save file: {e}")

# ==========================================
# 5. Main Execution
# ==========================================
def resolve_csv_path(script_dir: str) -> str:
    candidates = [
        os.path.join(script_dir, "student_record.csv"),
        os.path.join(script_dir, "ITE_Y3A2_Students.csv"),
        os.path.join(script_dir, "ITE_Y3A2_S1_Schedule.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return os.path.join(script_dir, "student_record.csv")


def ensure_csv_exists(csv_filename: str):
    if os.path.exists(csv_filename):
        return

    excel_candidates = [os.path.join(os.path.dirname(csv_filename), "student_record.xlsx")]
    for excel_file in excel_candidates:
        if os.path.exists(excel_file):
            import pandas as pd

            df = pd.read_excel(excel_file)
            missing_columns = set(REQUIRED_CSV_COLUMNS) - set(df.columns)
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise ValueError(f"Excel file is missing required student columns: {missing}")
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            load_students_from_csv(csv_filename)
            return

    raise FileNotFoundError(
        f"No student data file found. Place student_record.csv in {os.path.dirname(csv_filename)}."
    )


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_filename = resolve_csv_path(script_dir)
    try:
        ensure_csv_exists(csv_filename)
        students = load_students_from_csv(csv_filename)
        if not students:
            raise ValueError(f"No student records found in {csv_filename}.")
    except (OSError, ValueError, ImportError) as error:
        messagebox.showerror("Data Error", str(error))
        return

    # Start the App
    root = tk.Tk()
    app = AttendanceGUI(root, students, csv_filename)
    root.mainloop()

if __name__ == "__main__":
    main()