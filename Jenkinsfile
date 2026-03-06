
pipeline {
    agent any

    options {
        timeout(time: 20, unit: 'MINUTES')
    }

    environment {
        IMAGE_NAME = "acxcoldblood/dnotes"
        DEPLOY_DIR = "/opt/dnotes"
    }

    stages {

        /* ================================
           CHECKOUT SOURCE CODE
        ================================= */

        stage('Checkout') {
            steps {
                echo "Checking out repository..."
                checkout scm
                sh 'ls -la'
            }
        }

        /* ================================
           CI ENVIRONMENT PREPARATION
        ================================= */

        stage('Prepare CI Environment') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'db-creds',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'),
                    string(credentialsId: 'mysql-root-password', variable: 'MYSQL_ROOT'),
                    string(credentialsId: 'flask-secret', variable: 'FLASK_SECRET'),
                    string(credentialsId: 'smtp-user', variable: 'SMTP_USER'),
                    string(credentialsId: 'smtp-password', variable: 'SMTP_PASS')
                ]) {

                    sh '''
echo "Cleaning old CI containers..."
docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v --remove-orphans || true

echo "Generating fresh CI .env file..."

cat > .env <<EOF
FLASK_ENV=development
FLASK_DEBUG=1
APP_NAME=DevOps Notes Manager

APP_HOST=0.0.0.0
APP_PORT=5000

DB_HOST=mysql
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=devops_notes

MYSQL_ROOT_PASSWORD=$MYSQL_ROOT
MYSQL_DATABASE=devops_notes
MYSQL_USER=$DB_USER
MYSQL_PASSWORD=$DB_PASSWORD

SECRET_KEY=$FLASK_SECRET

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASS
SMTP_USE_TLS=true
RESET_TOKEN_MAX_AGE=3600
EOF

echo "CI .env successfully generated"
'''
                }
            }
        }

        /* ================================
           BUILD DOCKER IMAGE
        ================================= */

        stage('Build Image') {
            steps {
                sh '''
echo "Building Docker images..."
docker compose -f docker-compose.yml -f docker-compose.ci.yml build
'''
            }
        }

        /* ================================
           START CI STACK
        ================================= */

        stage('Start CI Stack') {
            steps {
                sh '''
echo "Starting CI containers..."
docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d
'''
            }
        }

        /* ================================
           HEALTH CHECK
        ================================= */

        stage('Health Check') {
            steps {
                sh '''
echo "Waiting for application health..."

CONTAINER=$(docker compose -f docker-compose.yml -f docker-compose.ci.yml ps -q web)

for i in $(seq 1 10)
do
    STATUS=$(docker exec $CONTAINER curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health || true)

    if [ "$STATUS" = "200" ]; then
        echo "Application is healthy!"
        exit 0
    fi

    echo "Attempt $i failed (status: $STATUS)"
    sleep 5
done

echo "Health check failed!"
echo "Running containers:"
docker ps

echo "Container logs:"
docker logs $CONTAINER || true

echo "Compose logs:"
docker compose -f docker-compose.yml -f docker-compose.ci.yml logs

exit 1
'''
            }
        }

        /* ================================
           PUSH IMAGE TO DOCKER HUB
        ================================= */

        stage('Push Image to Docker Hub') {
            steps {

                sh """
echo "Tagging image..."
docker tag dnotes ${IMAGE_NAME}:${BUILD_NUMBER}
docker tag dnotes ${IMAGE_NAME}:latest
"""

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    sh """
echo "Logging into Docker Hub..."
echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin

echo "Pushing build tag..."
docker push ${IMAGE_NAME}:${BUILD_NUMBER}

echo "Pushing latest tag..."
docker push ${IMAGE_NAME}:latest

docker logout
"""
                }
            }
        }

        /* ================================
           DEPLOY TO LOCAL PRODUCTION
        ================================= */

        stage('Deploy to Local Production') {
            steps {

                withCredentials([
                    usernamePassword(credentialsId: 'db-creds',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'),
                    string(credentialsId: 'mysql-root-password', variable: 'MYSQL_ROOT'),
                    string(credentialsId: 'flask-secret', variable: 'FLASK_SECRET'),
                    string(credentialsId: 'smtp-user', variable: 'SMTP_USER'),
                    string(credentialsId: 'smtp-password', variable: 'SMTP_PASS')
                ]) {

                    sh '''
echo "Preparing production directory..."
mkdir -p $DEPLOY_DIR

echo "Copying compose files..."
cp docker-compose.yml $DEPLOY_DIR/
cp docker-compose.prod.yml $DEPLOY_DIR/
cp -r nginx $DEPLOY_DIR/

cd $DEPLOY_DIR

echo "Generating production .env..."

cat > .env <<EOF
DB_HOST=mysql
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=devops_notes

MYSQL_ROOT_PASSWORD=$MYSQL_ROOT
MYSQL_DATABASE=devops_notes
MYSQL_USER=$DB_USER
MYSQL_PASSWORD=$DB_PASSWORD

SECRET_KEY=$FLASK_SECRET

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASS
SMTP_USE_TLS=true
RESET_TOKEN_MAX_AGE=3600
EOF

echo "Exporting image tag..."
export IMAGE_TAG=${BUILD_NUMBER}

echo "Stopping old production stack..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml down --remove-orphans || true

echo "Pulling latest image..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull

echo "Starting production stack..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "Production deployment completed successfully."
'''
                }
            }
        }

        /* ================================
           VERIFY DEPLOYMENT
        ================================= */

        stage('Verify Production') {
            steps {
                sh '''
echo "Running containers:"
docker ps

echo "Production stack status:"
docker compose -f /opt/dnotes/docker-compose.yml -f /opt/dnotes/docker-compose.prod.yml ps
'''
            }
        }
    }

    /* ================================
       CLEANUP CI STACK
    ================================= */

    post {
        always {
            sh '''
echo "Cleaning up CI containers..."
docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v --remove-orphans || true
'''
        }
    }
}

