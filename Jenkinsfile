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
                    // Still using the plugin here because it successfully worked in the last run!
                    appImage = docker.build("${DOCKER_IMAGE}:${APP_VERSION}")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to remote registry...'
                // BULLETPROOF FIX: Bypassing the buggy Docker Plugin entirely and using native shell commands.
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE}:${APP_VERSION}"
                    sh "docker tag ${DOCKER_IMAGE}:${APP_VERSION} ${DOCKER_IMAGE}:latest"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }
    }
}