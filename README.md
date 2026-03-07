# ACEest Fitness & Performance Platform (v3.0.1)

## Project Overview
ACEest v3.0.1 is a comprehensive fitness management platform driven by a robust relational database. Moving beyond basic weekly tracking, this version introduces advanced body metrics, BMI risk assessments, and deep session-level workout and exercise logging. It maintains visual analytics support to provide graphical insights into user performance and weight trends over time.

---

## Technical Stack
* **Framework**: Flask (Python 3.11)
* **Database**: SQLite3 
  * *Relational Schema*: `clients`, `progress`, `metrics`, `workouts`, `exercises`
* **Visualization**: Matplotlib Integration (Client-side)
* **CI/CD**: Jenkins (Local Quality Gate) & GitHub Actions (Cloud Validation)

---

## Automated Validation
Execute the test suite to verify the relational data lifecycle, isolation integrity, and API endpoints:
```bash
pytest