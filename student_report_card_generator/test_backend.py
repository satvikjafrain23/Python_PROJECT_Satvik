"""
Unit tests for Student Report Card Generator backend.
Tests calculations, topper logic, file export, and exception handling.
"""

import unittest
from models import Student
from storage import ReportCardStorage
from exceptions import (
    InvalidMarksError, NonNumericValueError, DuplicateRollNumberError, EmptyFieldError
)

class TestStudentReportCard(unittest.TestCase):

    def test_student_valid_calculations(self):
        marks = {"Math": 90, "Science": 80, "English": 85, "History": 75, "CS": 95}
        student = Student(
            name="John Doe",
            roll_number="R001",
            class_name="Class 10",
            marks=marks
        )
        self.assertEqual(student.total_marks, 425.0)
        self.assertEqual(student.percentage, 85.0)
        self.assertEqual(student.grade, "A")
        self.assertEqual(student.status, "PASSED")

    def test_invalid_marks_negative_exception(self):
        marks = {"Math": -15, "Science": 80}
        with self.assertRaises(InvalidMarksError) as ctx:
            Student("Test Student", "R002", "Class 10", marks)
        self.assertIn("between 0 and 100", str(ctx.exception))

    def test_invalid_marks_exceed_100_exception(self):
        marks = {"Math": 105, "Science": 80}
        with self.assertRaises(InvalidMarksError) as ctx:
            Student("Test Student", "R003", "Class 10", marks)
        self.assertIn("between 0 and 100", str(ctx.exception))

    def test_non_numeric_marks_exception(self):
        marks = {"Math": "ninety", "Science": 80}
        with self.assertRaises(NonNumericValueError) as ctx:
            Student("Test Student", "R004", "Class 10", marks)
        self.assertIn("valid number", str(ctx.exception))

    def test_empty_field_exception(self):
        marks = {"Math": 90}
        with self.assertRaises(EmptyFieldError) as ctx:
            Student("", "R005", "Class 10", marks)
        self.assertIn("Student Name", str(ctx.exception))

    def test_failed_status(self):
        # Even if average is high, single subject < 33 causes FAILED
        marks = {"Math": 100, "Science": 20, "English": 90}
        student = Student("Failed Student", "R006", "Class 10", marks)
        self.assertEqual(student.status, "FAILED")

    def test_topper_detection(self):
        storage = ReportCardStorage(data_dir="test_data")
        storage.students.clear()

        s1 = Student("Alice", "T001", "10A", {"Math": 90, "Science": 90})
        s2 = Student("Bob", "T002", "10A", {"Math": 99, "Science": 98}) # Topper!
        s3 = Student("Charlie", "T003", "10A", {"Math": 70, "Science": 75})

        storage.add_student(s1)
        storage.add_student(s2)
        storage.add_student(s3)

        topper = storage.get_topper()
        self.assertIsNotNone(topper)
        self.assertEqual(topper.roll_number, "T002")
        self.assertEqual(topper.name, "Bob")

        # Cleanup test data directory
        import shutil
        shutil.rmtree("test_data", ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
