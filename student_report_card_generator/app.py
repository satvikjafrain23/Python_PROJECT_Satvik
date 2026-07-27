"""
Flask Application Server & REST API for Student Report Card Generator.
Exposes routes for student management, topper statistics, report generation, and custom exception handling.
"""

from flask import Flask, render_template, request, jsonify, Response, send_file
import os
from models import Student
from storage import ReportCardStorage
from exceptions import (
    ReportCardException, InvalidMarksError, NonNumericValueError,
    DuplicateRollNumberError, EmptyFieldError
)

app = Flask(__name__, template_folder="templates", static_folder="static")
storage = ReportCardStorage(data_dir=os.path.join(os.path.dirname(__file__), "data"))


# Exception handlers to convert custom exceptions into JSON API responses
@app.errorhandler(ReportCardException)
def handle_report_card_exception(error: ReportCardException):
    return jsonify({
        "success": False,
        "error_type": error.__class__.__name__,
        "error": error.message
    }), error.status_code



@app.route("/")
def index():
    """Renders the main single-page web application UI."""
    return render_template("index.html")


@app.route("/api/students", methods=["GET"])
def get_students():
    """Returns all student report records along with class statistics and topper info."""
    students = [s.to_dict() for s in storage.get_all_students()]
    stats = storage.get_class_stats()
    return jsonify({
        "success": True,
        "students": students,
        "stats": stats
    })


@app.route("/api/students", methods=["POST"])
def add_student():
    """
    Adds a new student report card.
    Triggers custom Python exceptions (InvalidMarksError, NonNumericValueError, DuplicateRollNumberError, EmptyFieldError).
    """
    data = request.get_json(force=True) or {}
    
    # Extract fields
    name = data.get("name", "")
    roll_number = data.get("roll_number", "")
    class_name = data.get("class_name", "")
    gender = data.get("gender", "Not Specified")
    dob = data.get("dob", "")
    marks = data.get("marks", {})

    # Student constructor enforces all validation rules and throws exceptions
    new_student = Student(
        name=name,
        roll_number=roll_number,
        class_name=class_name,
        marks=marks,
        gender=gender,
        dob=dob
    )

    # Save to storage (checks for duplicate roll numbers)
    storage.add_student(new_student)

    return jsonify({
        "success": True,
        "message": f"Student '{new_student.name}' report card generated successfully!",
        "student": new_student.to_dict(),
        "stats": storage.get_class_stats()
    }), 201


@app.route("/api/students/<roll_number>", methods=["DELETE"])
def delete_student(roll_number):
    """Deletes a student record by Roll Number."""
    success = storage.delete_student(roll_number)
    if not success:
        return jsonify({
            "success": False,
            "error": f"Student with Roll Number '{roll_number}' not found."
        }), 404

    return jsonify({
        "success": True,
        "message": f"Roll Number '{roll_number}' deleted successfully.",
        "stats": storage.get_class_stats()
    })


@app.route("/api/students/<roll_number>/report", methods=["GET"])
def get_student_report_html(roll_number):
    """Returns rendered HTML report card for viewing or printing."""
    html_content = storage.generate_html_report_card(roll_number)
    if not html_content:
        return jsonify({"success": False, "error": "Student not found"}), 404

    return Response(html_content, mimetype="text/html")


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Serves downloadable CSV report card file."""
    csv_file = storage.export_to_csv()
    return send_file(
        csv_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name="students_report_summary.csv"
    )


@app.route("/api/export/json", methods=["GET"])
def export_json():
    """Serves downloadable JSON report cards backup file."""
    json_file = storage.json_path
    if not os.path.exists(json_file):
        storage.save_students()
    return send_file(
        json_file,
        mimetype="application/json",
        as_attachment=True,
        download_name="students_backup.json"
    )


if __name__ == "__main__":
    print("[+] Starting Student Report Card Generator Web Server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)

