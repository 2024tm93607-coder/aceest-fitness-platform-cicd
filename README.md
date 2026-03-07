# ACEest Fitness & Performance Platform (v3.2.4)

## Project Overview
ACEest v3.2.4 is a comprehensive fitness management platform featuring a robust relational database. It includes Role-Based Access Control (RBAC), advanced body metrics, BMI risk assessments, template-based AI-driven workout generation, comprehensive membership/billing tracking, and automated PDF client reporting capabilities.

---

## 1. Local Setup and Execution Instructions 
To run this application locally, ensure you have Python 3.11+ installed.

**Step 1: Clone the repository**
```bash
git clone <your-github-repo-url>
cd <repository-folder>

Step 2: Create and activate a virtual environment
# Windows
python -m venv venv
venv\Scripts\activate
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

Step 3: Install dependencies
pip install -r requirements.txt

Step 4: Execute the application
python app.py

The Flask server will start on http://127.0.0.1:5000. The SQLite database (aceest_fitness_v8.db) will be generated automatically upon initialization.

## 2. Steps to Run Tests Manually
This application uses pytest to validate application integrity, database isolation, and API routing.
Ensure your virtual environment is active and dependencies are installed.
Run the test suite from the root directory:
pytest

The test suite utilizes a clean-room database fixture to ensure zero state contamination between tests.

3. CI/CD Integration Logic (Jenkins & GitHub Actions)
This project employs a dual-pipeline Continuous Integration and Continuous Deployment (CI/CD) strategy to ensure code quality and deployment readiness.

Jenkins (Local Quality Gate): Jenkins is configured locally and bridged to GitHub via an Ngrok Webhook. Whenever code is pushed to the main branch, GitHub sends a payload to the Ngrok tunnel, triggering Jenkins. Jenkins automatically pulls the latest code, sets up a virtual environment, installs dependencies, and executes the automated test suite to verify application logic before further deployment.

GitHub Actions (Cloud Validation & Assembly): Concurrently, a GitHub Actions workflow (.github/workflows/main.yml) is triggered on every push or pull request. This cloud pipeline spins up an Ubuntu environment, installs Python 3.11, lints the code, builds the Docker image (Dockerfile), and executes the pytest suite inside the containerized environment. This guarantees "write once, run anywhere" consistency.