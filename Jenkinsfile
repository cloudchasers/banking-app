pipeline {
    agent any

    environment {
        REGISTRY = "cloudchasers.azurecr.io"
        IMAGE_NAME = "banking-app"
        TAG = "latest"
    }

    stages {

        stage('Checkout') {
            steps {
                git(
                    branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/cloudchasers/banking-app.git'
                )
            }
        }

    stage('Deploy to Dev EC2') {
    steps {
        sh '''
            ssh -o StrictHostKeyChecking=no \
            -i /var/lib/jenkins/.ssh/jenkins_deploy_key \
            ubuntu@44.222.238.61 \
            "
            cd /home/ubuntu/banking-app &&
            git pull &&
            docker compose down &&
            docker compose up -d --build
            "
        '''
    }
}

        
        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${TAG} .
                '''
            }
        }

        stage('Login to ACR') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'acr-creds',
                        usernameVariable: 'ACR_USER',
                        passwordVariable: 'ACR_PASS'
                    )
                ]) {
                    sh '''
                        echo "$ACR_PASS" | docker login ${REGISTRY} \
                          -u "$ACR_USER" \
                          --password-stdin
                    '''
                }
            }
        }

        stage('Tag Image') {
            steps {
                sh '''
                    docker tag ${IMAGE_NAME}:${TAG} \
                    ${REGISTRY}/${IMAGE_NAME}:${TAG}
                '''
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    docker push \
                    ${REGISTRY}/${IMAGE_NAME}:${TAG}
                '''
            }
        }
    }

    post {
        success {
            echo 'Image successfully pushed to ACR'
        }

        failure {
            echo 'Pipeline failed'
        }
    }
}
