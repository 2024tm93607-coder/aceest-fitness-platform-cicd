pipeline {
    agent any

    tools {
        dockerTool 'my-docker'
    }

    environment {
        DOCKER_IMAGE = 'tanvideshpande81/aceest-fitness'
        APP_VERSION = 'v3.2.4'
        // This tells Jenkins to route Docker commands to your Windows host engine!
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
                echo 'Running Unit Tests...'
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                pytest -v
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
                        -Dsonar.python.version=3.11"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building container image...'
                script {
                    appImage = docker.build("${DOCKER_IMAGE}:${APP_VERSION}")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to remote registry...'
                script {
                    docker.withRegistry('', 'docker-hub-creds') {
                        appImage.push()
                        appImage.push('latest')
                    }
                }
            }
        }
    }
}