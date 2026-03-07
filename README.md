# ACEest Fitness & Performance Platform (v3.2.4)

## Project Overview
ACEest v3.2.4 is a comprehensive fitness management platform featuring a robust relational database. It includes Role-Based Access Control (RBAC), advanced body metrics, BMI risk assessments, template-based AI-driven workout generation, comprehensive membership/billing tracking, and automated PDF client reporting capabilities.

---

## Technical Stack
* **Framework**: Flask (Python 3.11)
* **Database**: SQLite3 (`users`, `clients`, `progress`, `metrics`, `workouts`, `exercises`)
* **Features**: AI Template Generation, Matplotlib Analytics, FPDF Reporting, Membership Tracking
* **CI/CD**: Jenkins & GitHub Actions

---

## Automated Validation
Execute the full comprehensive test suite to verify application integrity and isolation:
```bash
pytest