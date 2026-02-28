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
        docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v || true

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