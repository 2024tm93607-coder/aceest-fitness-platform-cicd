pipeline {
    agent any

    tools {
        dockerTool 'my-docker'
    }

    environment {
        DOCKER_IMAGE = 'tanvideshpande81/aceest-fitness'
        APP_VERSION = 'v3.2.4'
        DOCKER_HOST = 'tcp://host.docker.internal:2375'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Quality Gate: Pytest') {
            steps {
                echo 'Running local unit tests...'
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                pytest -v --cov=. --cov-report=xml
                '''
            }
        }

        stage('Static Analysis: SonarQube') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=aceest-fitness \
                        -Dsonar.sources=. \
                        -Dsonar.python.version=3.11 \
                        -Dsonar.python.coverage.reportPaths=coverage.xml"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building container image...'
                script {
                    def appImage = docker.build("${DOCKER_IMAGE}:${APP_VERSION}")
                }
            }
        }

        stage('Containerized Validation') {
            steps {
                echo 'Executing tests inside the containerized environment...'
                sh "docker run --rm ${DOCKER_IMAGE}:${APP_VERSION} pytest"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to remote registry...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}"
                    sh "docker push ${DOCKER_IMAGE}:${APP_VERSION}"
                    sh "docker tag ${DOCKER_IMAGE}:${APP_VERSION} ${DOCKER_IMAGE}:latest"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully. Ready for Kubernetes deployment.'
        }
        failure {
            echo 'Pipeline failed. Check the console output for troubleshooting.'
        }
    }
}