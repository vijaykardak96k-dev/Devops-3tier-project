pipeline {
    agent any

    environment {
        BACKEND_IMAGE  = "vijaykardak/visitor-backend:v${BUILD_NUMBER}"
        FRONTEND_IMAGE = "vijaykardak/visitor-frontend:v${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "Pulling latest code from GitHub"
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "Building Backend Docker Image"
                dir('backend') {
                    sh "docker build -t ${BACKEND_IMAGE} ."
                }

                echo "Building Frontend Docker Image"
                dir('frontend') {
                    sh "docker build --no-cache -t ${FRONTEND_IMAGE} ."
                }
            }
        }

        stage('Trivy Security Scan') {
            steps {
                echo "Scanning Docker Images"
                sh """
                trivy image --severity HIGH,CRITICAL --exit-code 0 ${BACKEND_IMAGE}
                trivy image --severity HIGH,CRITICAL --exit-code 0 ${FRONTEND_IMAGE}
                """
            }
        }

        stage('DockerHub Login & Push') {
            steps {
                echo "Pushing Images to DockerHub"
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-hub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh """
                    echo '${DOCKER_PASS}' | docker login -u '${DOCKER_USER}' --password-stdin
                    docker push ${BACKEND_IMAGE}
                    docker push ${FRONTEND_IMAGE}
                    """
                }
            }
        }

        stage('Deploy To kOps Kubernetes') {
            steps {
                echo "Deploying/Creating all Application Resources on Kubernetes"
                dir('Deployment') {
                    sh """
                    kubectl apply -f maria-secret.yml
                    kubectl apply -f mariadb-init-configmap.yml
                    kubectl apply -f mariadb-headless-service.yml
                    kubectl apply -f backend-service.yml
                    kubectl apply -f frontend-service.yml
                    kubectl apply -f mariadb-statefulset.yml

                    envsubst < backend-deployment.yml | kubectl apply -f -
                    envsubst < frontend-deployment.yml | kubectl apply -f -
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo "Checking Kubernetes Rollout"
                sh """
                kubectl rollout status deployment/backend
                kubectl rollout status deployment/frontend
                kubectl get pods
                kubectl get svc
                """
            }
        }
    }

    post {
        success {
            echo """
            ======================================
            🚀 DEPLOYMENT SUCCESSFUL 🚀

            Backend Image:  ${BACKEND_IMAGE}
            Frontend Image: ${FRONTEND_IMAGE}
            Kubernetes:     kOps Cluster
            ======================================
            """
        }

        failure {
            echo """
            ======================================
            ❌ DEPLOYMENT FAILED ❌

            Check Jenkins Console Output
            ======================================
            """
        }

        always {
            echo "Cleaning Workspace"
            cleanWs()
        }
    }
}
