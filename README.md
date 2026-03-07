# ACEest Fitness & Performance Platform (v2.1.2)

## Project Overview
ACEest v2.1.2 transitions the platform into a relational data system. It implements a dual-table SQLite architecture to maintain separate records for Client Profiles and Weekly Adherence Progress, ensuring a complete historical record of fitness performance.

---

## Technical Stack
* **Framework**: Flask (Python 3.11)
* **Database**: SQLite3 (Relational Schema: `clients` & `progress` tables)
* **CI/CD**: Jenkins (Local Quality Gate) & GitHub Actions (Cloud Validation)

---

## Automated Validation
Execute the test suite to verify the relational data lifecycle:
```bash
pytest