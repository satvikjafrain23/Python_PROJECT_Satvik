/**
 * Student Report Card Generator - Frontend Application Logic
 * Interacts with Python Flask REST API, manages theme, live validation, toasts & report cards.
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    let studentsState = [];
    let statsState = {};

    // Elements
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const addStudentForm = document.getElementById('add-student-form');
    const studentTableBody = document.getElementById('student-table-body');
    const searchInput = document.getElementById('search-input');
    const addSubjectBtn = document.getElementById('add-subject-btn');
    const subjectsContainer = document.getElementById('subjects-container');
    const toastContainer = document.getElementById('toast-container');

    // Dashboard Stats Elements
    const statTotalStudents = document.getElementById('stat-total-students');
    const statClassAverage = document.getElementById('stat-class-average');
    const statPassRate = document.getElementById('stat-pass-rate');
    const topperName = document.getElementById('topper-name');
    const topperSub = document.getElementById('topper-sub');

    // Modal Elements
    const reportModal = document.getElementById('report-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const closeModalFooterBtn = document.getElementById('close-modal-footer-btn');
    const printModalBtn = document.getElementById('print-modal-btn');
    const modalBody = document.getElementById('modal-body');
    let currentModalRoll = null;

    // --- 1. Theme Toggle ---
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        themeToggleBtn.innerHTML = theme === 'dark' 
            ? '<i class="fa-solid fa-sun"></i>' 
            : '<i class="fa-solid fa-moon"></i>';
    }

    // --- 2. Toast Notifications ---
    function showToast(message, type = 'error') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const icon = type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-check';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;

        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // --- 3. Dynamic Subject Addition ---
    let customSubjectCount = 0;
    addSubjectBtn.addEventListener('click', () => {
        customSubjectCount++;
        const subjectName = prompt("Enter Subject Name (e.g. Physics, Economics, Hindi):");
        if (!subjectName || !subjectName.trim()) return;

        const sanitizedName = subjectName.trim();
        const fieldId = `mark-custom-${customSubjectCount}`;

        const card = document.createElement('div');
        card.className = 'subject-input-card';
        card.innerHTML = `
            <button type="button" class="btn-remove-subject" title="Remove Subject">&times;</button>
            <label for="${fieldId}">${sanitizedName}</label>
            <input type="number" id="${fieldId}" class="mark-field" data-subject="${sanitizedName}" min="0" max="100" placeholder="0 - 100">
        `;

        card.querySelector('.btn-remove-subject').addEventListener('click', () => card.remove());
        subjectsContainer.appendChild(card);
    });

    // --- 4. Fetch & Load Students ---
    async function fetchStudents() {
        try {
            const response = await fetch('/api/students');
            const data = await response.json();
            if (data.success) {
                studentsState = data.students || [];
                statsState = data.stats || {};
                renderDashboardStats(statsState);
                renderTable(studentsState);
            }
        } catch (error) {
            console.error('Error fetching students:', error);
            showToast('Failed to connect to backend server.', 'error');
        }
    }

    // --- 5. Render Dashboard & Topper Spotlight ---
    function renderDashboardStats(stats) {
        statTotalStudents.textContent = stats.total_students || 0;
        statClassAverage.textContent = `${stats.class_average_percentage || 0}%`;
        statPassRate.textContent = `${stats.pass_rate_percentage || 0}%`;

        const topper = stats.topper;
        if (topper) {
            topperName.textContent = topper.name;
            topperSub.textContent = `Score: ${topper.percentage}% (${topper.total_marks}/${topper.max_marks}) | Roll: ${topper.roll_number}`;
        } else {
            topperName.textContent = '--';
            topperSub.textContent = 'No records available yet.';
        }
    }

    // --- 6. Render Student Table ---
    function renderTable(students) {
        if (!students || students.length === 0) {
            studentTableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted pad-30">
                        <i class="fa-solid fa-folder-open fa-2x"></i>
                        <p class="mt-10">No student report cards found. Add a student above!</p>
                    </td>
                </tr>
            `;
            return;
        }

        const topper = statsState.topper;

        studentTableBody.innerHTML = students.map(s => {
            const isTopper = topper && topper.roll_number === s.roll_number;
            const topperBadge = isTopper ? '<span title="Class Topper" style="margin-left: 6px; color: #f59e0b;">🏆</span>' : '';
            const gradeClass = getGradeCSSClass(s.grade);
            const statusClass = s.status === 'PASSED' ? 'status-passed' : 'status-failed';

            return `
                <tr>
                    <td style="font-weight: 700;">${s.roll_number}</td>
                    <td style="font-weight: 600;">${s.name} ${topperBadge}</td>
                    <td>${s.class_name}</td>
                    <td><strong>${s.total_marks}</strong> / ${s.max_marks}</td>
                    <td><strong>${s.percentage}%</strong></td>
                    <td><span class="grade-badge ${gradeClass}">${s.grade}</span></td>
                    <td><span class="status-badge ${statusClass}">${s.status}</span></td>
                    <td>
                        <div class="action-btn-group">
                            <button class="btn-table-action btn-view" onclick="openReportModal('${s.roll_number}')" title="View & Print Report Card">
                                <i class="fa-solid fa-eye"></i>
                            </button>
                            <button class="btn-table-action btn-delete" onclick="deleteStudent('${s.roll_number}', '${s.name}')" title="Delete Record">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function getGradeCSSClass(grade) {
        switch (grade) {
            case 'A+': return 'grade-aplus';
            case 'A': return 'grade-a';
            case 'B': return 'grade-b';
            case 'C': return 'grade-c';
            case 'D': return 'grade-d';
            default: return 'grade-f';
        }
    }

    // --- 7. Search Filter ---
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderTable(studentsState);
            return;
        }
        const filtered = studentsState.filter(s => 
            s.name.toLowerCase().includes(query) || 
            s.roll_number.toLowerCase().includes(query) ||
            s.class_name.toLowerCase().includes(query)
        );
        renderTable(filtered);
    });

    // --- 8. Add Student Form Submission & Exception Handling ---
    addStudentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('input-name').value.trim();
        const roll_number = document.getElementById('input-roll').value.trim();
        const class_name = document.getElementById('input-class').value.trim();
        const gender = document.getElementById('input-gender').value;

        // Collect marks
        const markFields = document.querySelectorAll('.mark-field');
        const marks = {};
        let hasInvalidField = false;

        markFields.forEach(field => {
            field.classList.remove('is-invalid');
            const subject = field.getAttribute('data-subject');
            const val = field.value.trim();

            if (val !== '') {
                const num = Number(val);
                if (isNaN(num) || num < 0 || num > 100) {
                    field.classList.add('is-invalid');
                    hasInvalidField = true;
                }
                marks[subject] = val; // Pass string or number to let backend test custom exception!
            }
        });

        if (hasInvalidField) {
            showToast("Invalid marks entered! Marks must be numbers between 0 and 100.", "error");
            return;
        }

        const payload = { name, roll_number, class_name, gender, marks };

        try {
            const response = await fetch('/api/students', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                // Caught custom exception from backend!
                const errorMsg = result.error || "Failed to create student report.";
                showToast(`[${result.error_type || 'Error'}] ${errorMsg}`, "error");
                return;
            }

            // Success!
            showToast(result.message || "Student report card generated!", "success");
            addStudentForm.reset();
            // Restore default class name
            document.getElementById('input-class').value = "Class 10-A";
            fetchStudents();

        } catch (error) {
            console.error("Submission error:", error);
            showToast("An unexpected network error occurred.", "error");
        }
    });

    // --- 9. Delete Student ---
    window.deleteStudent = async function(rollNumber, name) {
        if (!confirm(`Are you sure you want to delete report card for ${name} (Roll: ${rollNumber})?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/students/${rollNumber}`, { method: 'DELETE' });
            const result = await response.json();

            if (result.success) {
                showToast(`Student ${name} deleted successfully.`, "success");
                fetchStudents();
            } else {
                showToast(result.error || "Failed to delete student.", "error");
            }
        } catch (error) {
            showToast("Network error deleting student.", "error");
        }
    };

    // --- 10. Report Modal Viewer & Print ---
    window.openReportModal = async function(rollNumber) {
        currentModalRoll = rollNumber;
        modalBody.innerHTML = '<div class="text-center pad-30"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><p class="mt-10">Rendering report card...</p></div>';
        reportModal.classList.add('active');

        try {
            const response = await fetch(`/api/students/${rollNumber}/report`);
            const html = await response.text();
            modalBody.innerHTML = html;
        } catch (error) {
            modalBody.innerHTML = '<div class="text-center pad-30 text-muted"><p>Error loading report card.</p></div>';
        }
    };

    closeModalBtn.addEventListener('click', () => reportModal.classList.remove('active'));
    closeModalFooterBtn.addEventListener('click', () => reportModal.classList.remove('active'));
    reportModal.addEventListener('click', (e) => {
        if (e.target === reportModal) reportModal.classList.remove('active');
    });

    printModalBtn.addEventListener('click', () => {
        if (!currentModalRoll) return;
        const printWindow = window.open(`/api/students/${currentModalRoll}/report`, '_blank');
        printWindow.onload = () => {
            printWindow.print();
        };
    });

    // Initialize
    fetchStudents();
});
