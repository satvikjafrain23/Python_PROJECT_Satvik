"""
Custom Exception Classes for Student Report Card Generator.
Used to handle invalid inputs, mark boundaries, empty fields, and duplicate records.
"""

class ReportCardException(Exception):
    """Base exception class for all report card errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidMarksError(ReportCardException):
    """Raised when marks are out of the valid 0 - 100 range."""
    def __init__(self, subject: str, value: float):
        message = f"Invalid marks for '{subject}': {value}. Marks must be between 0 and 100."
        super().__init__(message)
        self.subject = subject
        self.value = value


class NonNumericValueError(ReportCardException):
    """Raised when marks or numerical fields contain non-numeric data."""
    def __init__(self, field_name: str, value: str):
        message = f"Invalid numeric value for '{field_name}': '{value}'. Please enter a valid number."
        super().__init__(message)
        self.field_name = field_name
        self.value = value


class DuplicateRollNumberError(ReportCardException):
    """Raised when trying to add a student with a Roll Number that already exists."""
    def __init__(self, roll_number: str):
        message = f"Roll Number '{roll_number}' already exists. Roll numbers must be unique."
        super().__init__(message)
        self.roll_number = roll_number


class EmptyFieldError(ReportCardException):
    """Raised when required fields (like Name or Roll Number) are missing or blank."""
    def __init__(self, field_name: str):
        message = f"Field '{field_name}' cannot be empty."
        super().__init__(message)
        self.field_name = field_name
