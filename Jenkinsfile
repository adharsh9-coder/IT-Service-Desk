pipeline {
    agent any

    stages {
        stage('Checkout'){
            steps{
                checkout scm
            }
        }

        stage('Install Dependencies'){
            steps{
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Test'){
            steps {
                bat 'pytest'
            }
        }

        stage('Build Docker Image'){
            steps{
                bat 'docker build -t adharsh09/my-flask-app:latest .'
            }
        }

        stage('Push to Docker Hub') {
            steps{
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]){
                    bat '''
                        docker login -u "%DOCKER_USER%" -p "%DOCKER_PASS%"
                        docker push adharsh09/my-flask-app:latest
                    '''
                }
            }
        }
    }
}