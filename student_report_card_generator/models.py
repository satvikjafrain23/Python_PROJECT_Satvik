"""
Data models and calculation logic for Student Report Card Generator.
Handles student profile details, mark calculations, grades, and pass/fail status.
"""

from typing import Dict, List, Any
from exceptions import InvalidMarksError, NonNumericValueError, EmptyFieldError


class Student:
    """Represents a student record and calculates report card statistics."""

    DEFAULT_SUBJECTS = ["Mathematics", "Science", "English", "Social Studies", "Computer Science"]

    def __init__(self, name: str, roll_number: str, class_name: str, 
                 marks: Dict[str, Any], gender: str = "Not Specified", dob: str = ""):
        self.name = self._validate_name(name)
        self.roll_number = self._validate_roll_number(roll_number)
        self.class_name = self._validate_class(class_name)
        self.gender = gender or "Not Specified"
        self.dob = dob or ""
        self.marks: Dict[str, float] = self._validate_and_sanitize_marks(marks)
        
        # Calculate stats
        self.total_marks: float = self.calculate_total()
        self.max_marks: float = len(self.marks) * 100.0 if self.marks else 500.0
        self.percentage: float = self.calculate_percentage()
        self.grade: str = self.calculate_grade()
        self.status: str = self.calculate_status()

    @staticmethod
    def _validate_name(name: str) -> str:
        if not name or not name.strip():
            raise EmptyFieldError("Student Name")
        return name.strip()

    @staticmethod
    def _validate_roll_number(roll_number: str) -> str:
        if not roll_number or not str(roll_number).strip():
            raise EmptyFieldError("Roll Number")
        return str(roll_number).strip().upper()

    @staticmethod
    def _validate_class(class_name: str) -> str:
        if not class_name or not class_name.strip():
            raise EmptyFieldError("Class / Section")
        return class_name.strip()

    @staticmethod
    def _validate_and_sanitize_marks(raw_marks: Dict[str, Any]) -> Dict[str, float]:
        """Validates all subject marks and enforces 0-100 range and numerical checks."""
        if not raw_marks:
            raise EmptyFieldError("Subject Marks")

        sanitized = {}
        for subject, score in raw_marks.items():
            subject_name = str(subject).strip()
            if not subject_name:
                continue

            # Convert to float and validate type
            try:
                numeric_score = float(score)
            except (ValueError, TypeError):
                raise NonNumericValueError(subject_name, str(score))

            # Validate range [0, 100]
            if numeric_score < 0 or numeric_score > 100:
                raise InvalidMarksError(subject_name, numeric_score)

            sanitized[subject_name] = round(numeric_score, 2)

        if not sanitized:
            raise EmptyFieldError("Valid Subject Marks")

        return sanitized

    def calculate_total(self) -> float:
        """Calculates the sum of all subject marks."""
        return round(sum(self.marks.values()), 2)

    def calculate_percentage(self) -> float:
        """Calculates percentage based on total marks and total maximum marks."""
        if self.max_marks <= 0:
            return 0.0
        return round((self.total_marks / self.max_marks) * 100.0, 2)

    def calculate_grade(self) -> str:
        """Determines the letter grade based on overall percentage."""
        pct = self.percentage
        if pct >= 90.0:
            return "A+"
        elif pct >= 80.0:
            return "A"
        elif pct >= 70.0:
            return "B"
        elif pct >= 60.0:
            return "C"
        elif pct >= 50.0:
            return "D"
        else:
            return "F"

    def calculate_status(self) -> str:
        """
        Determines overall PASS or FAIL status.
        Student passes if overall percentage >= 33% AND all individual subject marks >= 33.
        """
        if self.percentage < 33.0:
            return "FAILED"

        for subject, score in self.marks.items():
            if score < 33.0:
                return "FAILED"

        return "PASSED"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes student object into a dictionary for JSON/CSV/API responses."""
        return {
            "name": self.name,
            "roll_number": self.roll_number,
            "class_name": self.class_name,
            "gender": self.gender,
            "dob": self.dob,
            "marks": self.marks,
            "total_marks": self.total_marks,
            "max_marks": self.max_marks,
            "percentage": self.percentage,
            "grade": self.grade,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """Creates a Student instance from a dictionary representation."""
        return cls(
            name=data.get("name", ""),
            roll_number=data.get("roll_number", ""),
            class_name=data.get("class_name", ""),
            marks=data.get("marks", {}),
            gender=data.get("gender", "Not Specified"),
            dob=data.get("dob", "")
        )
