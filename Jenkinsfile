pipeline {
    agent any

    stages {

        stage('Checkout confirmation') {
            steps {
                sh 'echo "Jenkins pipeline started on dev branch"'
                sh 'ls -la'
            }
        }

        stage('Prepare Environment') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'db-creds',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'
                    ),
                    string(credentialsId: 'mysql-root-password',
                           variable: 'MYSQL_ROOT'),
                    string(credentialsId: 'flask-secret',
                           variable: 'FLASK_SECRET'),
                    string(credentialsId: 'smtp-user',
                           variable: 'SMTP_USER'),
                    string(credentialsId: 'smtp-password',
                           variable: 'SMTP_PASS')
                ]) {
                    sh '''
                    echo "Cleaning old containers..."
                    docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v || true

                    echo "Generating fresh .env file..."

                    cat > .env <<EOF
# -----------------------------
# Application
# -----------------------------
FLASK_ENV=development
FLASK_DEBUG=1
APP_NAME=DevOps Notes Manager

# -----------------------------
# Server
# -----------------------------
APP_HOST=0.0.0.0
APP_PORT=5000

# -----------------------------
# Database (Flask)
# -----------------------------
DB_HOST=mysql
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=devops_notes

# -----------------------------
# MySQL (Docker init)
# -----------------------------
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT
MYSQL_DATABASE=devops_notes
MYSQL_USER=$DB_USER
MYSQL_PASSWORD=$DB_PASSWORD

# -----------------------------
# Security
# -----------------------------
SECRET_KEY=$FLASK_SECRET
SESSION_COOKIE_SECURE=false
REMEMBER_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=Lax
REMEMBER_COOKIE_SAMESITE=Lax
UPLOAD_MAX_MB=2

# -----------------------------
# Email
# -----------------------------
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASS
SMTP_USE_TLS=true
RESET_TOKEN_MAX_AGE=3600
EOF

                    echo ".env successfully generated"
                    '''
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                echo "Building Docker images..."
                docker compose -f docker-compose.yml -f docker-compose.ci.yml build
                '''
            }
        }

        stage('Start CI Containers') {
            steps {
                sh '''
                echo "Starting CI containers..."
                docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                echo "Waiting for application to be healthy..."

                for i in 1 2 3 4 5 6 7 8 9 10
                do
                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health || true)

                    if [ "$STATUS" = "200" ]
                    then
                        echo "Application is healthy!"
                        exit 0
                    fi

                    echo "Attempt $i failed with status $STATUS"
                    sleep 5
                done

                echo "Health check failed!"
                exit 1
                '''
            }
        }

        stage('Push Image') {
            steps {
                script {
                    def imageTag = "${BUILD_NUMBER}"
                    def imageName = "acxcoldblood/dnotes"

                    sh """
                        echo "Tagging image for Docker Hub..."
                        docker tag dnotes ${imageName}:${imageTag}
                        docker tag dnotes ${imageName}:latest
                    """
                }

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "Logging into Docker Hub..."
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin

                        echo "Pushing build number tag..."
                        docker push acxcoldblood/dnotes:${BUILD_NUMBER}

                        echo "Pushing latest tag..."
                        docker push acxcoldblood/dnotes:latest

                        docker logout
                    """
                }
            }
        }

        stage('Debug Logs') {
            steps {
                sh '''
                echo "Checking running containers..."
                docker ps

                echo "Flask container logs:"
                docker logs devops-flask || true
                '''
            }
        }
    }

    post {
        always {
            sh '''
            echo "Cleaning up containers..."
            docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v
            '''
        }
    }
}