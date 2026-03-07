# ACEest Fitness & Performance Platform (v2.2.1)

## Project Overview
ACEest v2.2.1 adds visual analytics support to the relational core. It enables historical progress retrieval for Matplotlib charting, allowing the system to provide graphical insights into user performance over time.

---

## Technical Stack
* **Framework**: Flask (Python 3.11)
* **Database**: SQLite3 (Relational Schema: `clients` & `progress` tables)
* **Visualization**: Matplotlib Integration (Client-side)
* **CI/CD**: Jenkins (Local Quality Gate) & GitHub Actions (Cloud Validation)

---

## Automated Validation
Execute the test suite to verify the relational data lifecycle and visualization API endpoints:
```bash
pytest