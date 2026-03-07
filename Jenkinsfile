pipeline {
    agent any
    stages {
        stage('Build & Environment Setup') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Quality Gate (Unit Testing)') {
            steps {
                sh '. venv/bin/activate && pytest'
            }
        }
    }
}