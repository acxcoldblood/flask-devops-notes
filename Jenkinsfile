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
    environment {
        DB_CREDS = credentials('db-creds')
        MYSQL_ROOT = credentials('mysql-root-password')
        FLASK_SECRET = credentials('flask-secret')
        SMTP_PASS = credentials('smtp-password')
        SMTP_USER = credentials('smtp-user')
    }
    steps {
        sh '''
        echo "Cleaning old containers..."
        docker compose -f docker-compose.ci.yml down -v || true

        echo "Creating .env from template..."
        cp .env.example .env

        echo "Injecting credentials into .env..."

        echo "DB_USER=${DB_CREDS_USR}" >> .env
        echo "DB_PASSWORD=${DB_CREDS_PSW}" >> .env

        echo "MYSQL_USER=${DB_CREDS_USR}" >> .env
        echo "MYSQL_PASSWORD=${DB_CREDS_PSW}" >> .env
        echo "MYSQL_ROOT_PASSWORD=${MYSQL_ROOT}" >> .env

        echo "SECRET_KEY=${FLASK_SECRET}" >> .env

        echo "SMTP_USER=${SMTP_USER}" >> .env
        echo "SMTP_PASSWORD=${SMTP_PASS}" >> .env

        echo ".env successfully generated"
        '''
    }
    }

    }
}