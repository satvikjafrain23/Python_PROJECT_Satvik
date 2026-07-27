"""
Storage and Report Persistence Manager.
Handles JSON storage, CSV export, class analytics, topper detection, and HTML report card generation.
"""

import json
import csv
import os
from typing import List, Dict, Optional, Any
from models import Student
from exceptions import DuplicateRollNumberError


class ReportCardStorage:
    """Manages student records storage in JSON, CSV exports, topper detection, and statistics."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.json_path = os.path.join(self.data_dir, "students.json")
        self.csv_path = os.path.join(self.data_dir, "students_summary.csv")
        self.students: Dict[str, Student] = {}
        self._ensure_dir()
        self.load_students()

    def _ensure_dir(self):
        """Creates data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def load_students(self) -> Dict[str, Student]:
        """Loads student records from JSON file."""
        if not os.path.exists(self.json_path):
            self.students = {}
            # Pre-seed sample data if empty so the user can immediately test the dashboard!
            self._seed_sample_data()
            return self.students

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.students = {}
                for item in data:
                    try:
                        student = Student.from_dict(item)
                        self.students[student.roll_number] = student
                    except Exception as e:
                        print(f"Skipping corrupted record: {e}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading JSON data: {e}")
            self.students = {}

        return self.students

    def save_students(self):
        """Saves current student records to JSON file and updates CSV summary."""
        self._ensure_dir()
        # Save JSON
        data = [s.to_dict() for s in self.students.values()]
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        # Update CSV
        self.export_to_csv()

    def add_student(self, student: Student) -> Student:
        """Adds a student record. Raises DuplicateRollNumberError if roll number exists."""
        if student.roll_number in self.students:
            raise DuplicateRollNumberError(student.roll_number)

        self.students[student.roll_number] = student
        self.save_students()
        return student

    def update_student(self, student: Student) -> Student:
        """Updates an existing student record."""
        self.students[student.roll_number] = student
        self.save_students()
        return student

    def delete_student(self, roll_number: str) -> bool:
        """Deletes a student record by roll number."""
        roll = roll_number.strip().upper()
        if roll in self.students:
            del self.students[roll]
            self.save_students()
            return True
        return False

    def get_student(self, roll_number: str) -> Optional[Student]:
        """Gets student by roll number."""
        return self.students.get(roll_number.strip().upper())

    def get_all_students(self) -> List[Student]:
        """Returns a list of all students sorted by Roll Number."""
        return sorted(list(self.students.values()), key=lambda s: s.roll_number)

    def get_topper(self) -> Optional[Student]:
        """
        Finds the top performing student (Highest Percentage / Total Marks).
        Faculty Requirement: Find Topper.
        """
        if not self.students:
            return None
        return max(self.students.values(), key=lambda s: (s.percentage, s.total_marks))

    def get_class_stats(self) -> Dict[str, Any]:
        """Calculates overall class summary statistics for the Dashboard."""
        total_count = len(self.students)
        if total_count == 0:
            return {
                "total_students": 0,
                "class_average_percentage": 0.0,
                "passed_count": 0,
                "failed_count": 0,
                "pass_rate_percentage": 0.0,
                "topper": None
            }

        percentages = [s.percentage for s in self.students.values()]
        class_avg = round(sum(percentages) / total_count, 2)
        passed_count = sum(1 for s in self.students.values() if s.status == "PASSED")
        failed_count = total_count - passed_count
        pass_rate = round((passed_count / total_count) * 100.0, 2)
        topper = self.get_topper()

        return {
            "total_students": total_count,
            "class_average_percentage": class_avg,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "pass_rate_percentage": pass_rate,
            "topper": topper.to_dict() if topper else None
        }

    def export_to_csv(self, filename: Optional[str] = None) -> str:
        """Exports all student records summary to CSV file."""
        target_path = filename or self.csv_path
        self._ensure_dir()

        students_list = self.get_all_students()
        if not students_list:
            headers = ["Roll Number", "Name", "Class", "Gender", "Total Marks", "Max Marks", "Percentage", "Grade", "Status"]
            with open(target_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            return target_path

        # Determine all unique subjects across students
        all_subjects = sorted(list({sub for s in students_list for sub in s.marks.keys()}))
        headers = ["Roll Number", "Name", "Class", "Gender"] + all_subjects + ["Total Marks", "Max Marks", "Percentage (%)", "Grade", "Status"]

        with open(target_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for s in students_list:
                row = [s.roll_number, s.name, s.class_name, s.gender]
                for sub in all_subjects:
                    row.append(s.marks.get(sub, "N/A"))
                row.extend([s.total_marks, s.max_marks, f"{s.percentage}%", s.grade, s.status])
                writer.writerow(row)

        return target_path

    def generate_html_report_card(self, roll_number: str) -> Optional[str]:
        """Generates a printable, beautifully styled HTML Report Card for a single student."""
        student = self.get_student(roll_number)
        if not student:
            return None

        topper = self.get_topper()
        is_topper = topper and topper.roll_number == student.roll_number

        subjects_html = ""
        for subject, score in student.marks.items():
            progress_width = min(100, max(0, score))
            color_class = "pass" if score >= 33 else "fail"
            subjects_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: 500;">{subject}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">100</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center; font-weight: 600;">{score}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                    <div style="background: #edf2f7; border-radius: 9999px; height: 10px; overflow: hidden; width: 100%;">
                        <div style="background: {'#10b981' if score >= 33 else '#ef4444'}; width: {progress_width}%; height: 100%;"></div>
                    </div>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">
                    <span style="padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; background: {'#d1fae5; color: #065f46;' if score >= 33 else '#fee2e2; color: #991b1b;'}">
                        {'PASS' if score >= 33 else 'FAIL'}
                    </span>
                </td>
            </tr>
            """

        topper_badge = """
        <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; font-weight: 700; margin-bottom: 15px; font-size: 14px;">
            🏆 CLASS TOPPER
        </div>
        """ if is_topper else ""

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Report Card - {student.name} ({student.roll_number})</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #1e293b; padding: 40px; margin: 0; }}
                .card {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); padding: 40px; border: 1px solid #e2e8f0; }}
                .header {{ border-bottom: 2px solid #6366f1; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
                .title {{ font-size: 28px; font-weight: 800; color: #4338ca; margin: 0; }}
                .subtitle {{ color: #64748b; font-size: 14px; margin-top: 4px; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; background: #f1f5f9; padding: 20px; border-radius: 12px; }}
                .info-label {{ font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px; }}
                .info-val {{ font-size: 16px; font-weight: 600; color: #0f172a; margin-top: 2px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                th {{ background: #4f46e5; color: white; padding: 14px 12px; text-align: left; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
                th:nth-child(2), th:nth-child(3), th:nth-child(5) {{ text-align: center; }}
                .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; background: #e0e7ff; padding: 20px; border-radius: 12px; text-align: center; }}
                .sum-val {{ font-size: 22px; font-weight: 800; color: #3730a3; }}
                .sum-label {{ font-size: 12px; font-weight: 600; color: #4338ca; text-transform: uppercase; margin-top: 4px; }}
                .grade-badge {{ font-size: 26px; font-weight: 900; color: #4338ca; }}
                .status-pass {{ color: #059669; font-weight: 800; }}
                .status-fail {{ color: #dc2626; font-weight: 800; }}
                @media print {{ body {{ background: white; padding: 0; }} .card {{ box-shadow: none; border: none; }} }}
            </style>
        </head>
        <body>
            <div class="card">
                {topper_badge}
                <div class="header">
                    <div>
                        <h1 class="title">STUDENT ACADEMIC REPORT CARD</h1>
                        <div class="subtitle">Official Performance & Evaluation Transcript</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="grade-badge">Grade: {student.grade}</div>
                        <div class="{'status-pass' if student.status == 'PASSED' else 'status-fail'}">{student.status}</div>
                    </div>
                </div>

                <div class="grid">
                    <div>
                        <div class="info-label">Student Name</div>
                        <div class="info-val">{student.name}</div>
                    </div>
                    <div>
                        <div class="info-label">Roll Number</div>
                        <div class="info-val">{student.roll_number}</div>
                    </div>
                    <div>
                        <div class="info-label">Class / Section</div>
                        <div class="info-val">{student.class_name}</div>
                    </div>
                    <div>
                        <div class="info-label">Gender</div>
                        <div class="info-val">{student.gender}</div>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Max Marks</th>
                            <th>Marks Obtained</th>
                            <th style="width: 25%;">Performance</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {subjects_html}
                    </tbody>
                </table>

                <div class="summary">
                    <div>
                        <div class="sum-val">{student.total_marks} / {student.max_marks}</div>
                        <div class="sum-label">Total Score</div>
                    </div>
                    <div>
                        <div class="sum-val">{student.percentage}%</div>
                        <div class="sum-label">Percentage</div>
                    </div>
                    <div>
                        <div class="sum-val">{student.grade}</div>
                        <div class="sum-label">Final Grade</div>
                    </div>
                    <div>
                        <div class="sum-val" style="color: {'#059669' if student.status == 'PASSED' else '#dc2626'};">{student.status}</div>
                        <div class="sum-label">Result Status</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _seed_sample_data(self):
        """Seeds standard sample students so the application looks rich immediately."""
        sample_students = [
            Student(
                name="Aarav Sharma",
                roll_number="101",
                class_name="Class 10-A",
                gender="Male",
                marks={"Mathematics": 95, "Science": 92, "English": 88, "Social Studies": 90, "Computer Science": 98}
            ),
            Student(
                name="Priya Patel",
                roll_number="102",
                class_name="Class 10-A",
                gender="Female",
                marks={"Mathematics": 84, "Science": 79, "English": 86, "Social Studies": 80, "Computer Science": 90}
            ),
            Student(
                name="Rohan Verma",
                roll_number="103",
                class_name="Class 10-B",
                gender="Male",
                marks={"Mathematics": 65, "Science": 70, "English": 72, "Social Studies": 68, "Computer Science": 75}
            ),
            Student(
                name="Ananya Iyer",
                roll_number="104",
                class_name="Class 10-A",
                gender="Female",
                marks={"Mathematics": 98, "Science": 96, "English": 94, "Social Studies": 91, "Computer Science": 99}
            )
        ]
        for s in sample_students:
            self.students[s.roll_number] = s
        self.save_students()
