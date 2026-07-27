# 🎓 Student Report Card Generator (EduGrade Pro)

A modern, full-stack **Student Report Card Generator** built with **Python Flask** on the backend and an interactive **HTML5 / Vanilla CSS3 / ES6 JavaScript** web interface.

Designed specifically to meet all academic & faculty requirements:
1. **Add Student Details**: Full Name, Roll Number, Class/Section, Gender, and Date of Birth.
2. **Enter Marks**: Subject-wise mark inputs (Mathematics, Science, English, Social Studies, Computer Science + Custom Subjects).
3. **Automated Calculations**: Total Marks, Percentage, Letter Grade (`A+`, `A`, `B`, `C`, `D`, `F`), and Result Status (`PASSED` / `FAILED`).
4. **Topper Identification**: Class Topper Spotlight Card automatically calculates and displays the highest-scoring student.
5. **Report Files Export & Save**: Persistent JSON storage (`data/students.json`), CSV summary export (`data/students_summary.csv`), and printable HTML/PDF report cards.
6. **Robust Custom Exception Handling**: Custom Python exceptions validate inputs and trap invalid marks (`<0` or `>100`), non-numeric entries, empty required fields, and duplicate roll numbers with visual toast alerts.

---

## 🌟 Features Overview

- 🌙 **Dark & Light Mode**: Seamless theme switcher with persistent local storage.
- 📊 **Live Metric Dashboard**: Displays Total Students, Class Average %, Pass Rate %, and Topper Spotlight.
- ⚡ **Real-Time Exception Handling**: Frontend and Backend work together to highlight out-of-range mark fields and display descriptive error notifications.
- 🔍 **Instant Search & Filter**: Search student report records instantly by name, roll number, or class.
- 🖨️ **Printable Report Cards**: Generates official individual transcript report cards ready to print or save as PDF.
- 📥 **CSV & JSON Backup**: One-click download of class summary tables or complete JSON backups.

---

## 🛠️ Exception Hierarchy (`exceptions.py`)

```python
ReportCardException (Base)
├── InvalidMarksError        # Raised when marks < 0 or > 100
├── NonNumericValueError     # Raised when non-numeric values are passed for marks
├── DuplicateRollNumberError # Raised when adding a student with existing Roll Number
└── EmptyFieldError          # Raised when required fields (Name, Roll) are blank
```

---

## 📐 Evaluation & Grading Formula (`models.py`)

- **Total Marks**: $\sum \text{Subject Marks}$
- **Percentage**: $\frac{\text{Total Marks}}{\text{Max Possible Marks}} \times 100$
- **Grade Scale**:
  - $\ge 90\% \rightarrow \mathbf{A+}$
  - $\ge 80\% \rightarrow \mathbf{A}$
  - $\ge 70\% \rightarrow \mathbf{B}$
  - $\ge 60\% \rightarrow \mathbf{C}$
  - $\ge 50\% \rightarrow \mathbf{D}$
  - $< 50\% \rightarrow \mathbf{F}$
- **Pass/Fail Criteria**: Student passes if overall Percentage $\ge 33\%$ AND every individual subject score $\ge 33$.

---

## 🚀 How to Run

1. Open your terminal in the project directory:
   ```bash
   cd C:\Users\hp\.gemini\antigravity\scratch\student_report_card_generator
   ```

2. Run the unit tests:
   ```bash
   python test_backend.py
   ```

3. Launch the web application:
   ```bash
   python app.py
   ```

4. Open your web browser at:
   ```text
   http://127.0.0.1:5000
   ```
