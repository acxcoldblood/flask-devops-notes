DevOps Notes Manager

A Flask-based CRUD web application for managing DevOps commands and notes, fully containerized using Docker and Docker Compose with a MySQL backend.

This project is designed to practice real-world DevOps fundamentals such as containerization, service orchestration, environment-based configuration, and persistent storage.

📌 Features

Create, Read, Update, Delete (CRUD) DevOps notes

Flask backend with Jinja2 templates

MySQL database for persistent storage

Dockerized application

Multi-container setup using Docker Compose

Environment variables for secure configuration

Persistent data using Docker volumes

🛠 Tech Stack

Backend: Flask (Python)

Database: MySQL 8

Frontend: HTML, CSS (Jinja templates)

Containerization: Docker

Orchestration: Docker Compose

📂 Project Structure
devops-notes-manager/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
│
├── templates/
│ ├── index.html
│ └── edit.html
│
└── static/
└── css/
└── style.css

⚙️ Environment Variables

Create a .env file in the project root (do not commit it):

DB_HOST=mysql
DB_USER=root
DB_PASSWORD=rootpassword
DB_NAME=devops_notes

The .env file is excluded via .gitignore to keep credentials secure.

🐳 Docker Setup
1️⃣ Build and start containers
docker compose up --build

This command will:

Build the Flask application image

Start a MySQL container

Create a shared Docker network

Persist database data using Docker volumes

2️⃣ Access the application

Open your browser and navigate to:

http://localhost:5000

🗄 Database Initialization

The database is created automatically, but the notes table must exist.

Create table (one-time setup):
docker exec -it devops-mysql mysql -uroot -prootpassword devops_notes

CREATE TABLE notes (
id INT AUTO_INCREMENT PRIMARY KEY,
command VARCHAR(255) NOT NULL,
description TEXT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

🧠 DevOps Concepts Demonstrated

Container isolation and networking

Service discovery using Docker Compose

Environment-based configuration

Persistent storage with Docker volumes

Flask application binding for container access (0.0.0.0)

Separation of application and database layers

🛑 Stopping the Application

To stop all services:

docker compose down

To stop and remove volumes (clears DB data):

docker compose down -v

🚀 Future Enhancements

Automatic database table creation

Pagination for large datasets

Authentication and user roles

Production server using Gunicorn

CI/CD pipeline with GitHub Actions

Cloud deployment (AWS / Azure)

👨‍💻 Author

Kushagra Agarwal
DevOps & Cloud Enthusiast

⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.
