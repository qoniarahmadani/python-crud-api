pipeline {
    agent any

    environment {
        IMAGE_NAME = 'python-crud-api'
        CONTAINER_NAME = 'production-api-container'
        DATA_VOLUME = 'production-api-data'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Syntax Check') {
            steps {
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t python-crud-api:latest .'
            }
        }

        stage('Deployment') {
            steps {
                sh '''
                    docker stop production-api-container || true
                    docker rm production-api-container || true
                    docker volume create production-api-data
                    docker run -d \
                        --name production-api-container \
                        -p 5000:5000 \
                        -v production-api-data:/var/lib/backend_data \
                        python-crud-api:latest
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 5
                    curl -f http://host.docker.internal:5000/health
                '''
            }
        }
    }
}