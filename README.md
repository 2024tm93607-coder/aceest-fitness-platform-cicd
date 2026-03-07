# ACEest Fitness & Performance Platform (v3.1.2)

## Project Overview
ACEest v3.1.2 is a comprehensive fitness management platform featuring a robust relational database. It includes Role-Based Access Control (RBAC), advanced body metrics, BMI risk assessments, AI-driven workout generation, and automated PDF client reporting capabilities.

---

## Technical Stack
* **Framework**: Flask (Python 3.11)
* **Database**: SQLite3 (`users`, `clients`, `progress`, `metrics`, `workouts`, `exercises`)
* **Features**: AI Generation, Matplotlib Analytics, FPDF Reporting
* **CI/CD**: Jenkins & GitHub Actions

---

## Automated Validation
Execute the full comprehensive test suite to verify application integrity and isolation:
```bash
pytest