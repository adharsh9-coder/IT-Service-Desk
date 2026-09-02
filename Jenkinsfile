pipeline {
    agent any

    triggers{
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Test') {
            steps {
                bat '''
                    python --version
                    python -m pip install -r requirements.txt
                    python -m pytest
                '''
            }
        }
        stage('Build Docker Image') {
            steps {
                bat '''
                    docker build -t adharsh09/my-flask-app:latest .
                '''
            }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat '''
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        docker push adharsh09/my-flask-app:latest
                    '''
                }
            }
        }
    }

    post {
        success {
            emailext(
                subject: "SUCCESS ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Successful</h2>
                    <p><b>URL</b>: ${env.BUILD_URL}</p>
                """,
                to: "internadharsh9@gmail.com" 
            )
        }
        failure {
            emailext(
                subject: "FAILED ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Failed</h2>
                    <p><b>URL</b>: ${env.BUILD_URL}</p>
                """,
                to: "internadharsh9@gmail.com" 
            )
        }
    }
}