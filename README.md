text
![CI](https://github.com/acxcoldblood/flask-devops-notes/actions/workflows/ci.yml/badge.svg)

# DevOps Notes Manager

A Flask-based CRUD web application for managing DevOps commands and notes, fully containerized using Docker and Docker Compose with a MySQL backend and a production-style CI pipeline using GitHub Actions.

---

## 🏗 Architecture Overview

```text
Browser
   |
   v
Flask (Docker container)
   |
   v
MySQL (Docker container)

```
---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Database:** MySQL 8
- **Frontend:** HTML, CSS (Jinja2 templates)
- **Containerization:** Docker
- **Orchestration:** Docker Compose
- **CI/CD:** GitHub Actions

---

## 📂 Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── db.py
│   └── config.py
├── templates/
│   ├── index.html
│   └── edit.html
├── static/
│   └── css/
│       └── style.css
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .github/workflows/ci.yml

```
---


## ⚙️ Environment Variables

Create a `.env` file in the project root:

DB_HOST=mysql
DB_USER=example_user
DB_PASSWORD=example_password
DB_NAME=example_db
MYSQL_ROOT_PASSWORD=example_root_password


📌 `.env` is ignored via `.gitignore`.  
📌 `.env.example` is committed for CI and local setup reference.

---

## ▶️ Run Locally (Docker)

### Prerequisites

- Docker  
- Docker Compose  

### Steps

git clone https://github.com/<USERNAME>/<REPO_NAME>.git
cd <REPO_NAME>

cp .env.example .env
docker compose up --build


Application will be available at:

http://localhost:5000


---

## 🔄 CI Pipeline Overview

The GitHub Actions CI pipeline runs on every push to the `main` branch and performs:

- Checkout source code  
- Create runtime `.env` from `.env.example`  
- Build Docker images  
- Start services using Docker Compose  
- Wait for MySQL health check  
- Start Flask application  
- Validate application using `/health` endpoint  
- Cleanly shut down containers  

This ensures the application is buildable, runnable, and healthy on every commit.

---

## 🧪 Health Check Endpoint

The application exposes a lightweight health endpoint used by CI:

GET /health

Response:

200 OK

This avoids fragile checks against UI routes.

---

## 🧠 DevOps Concepts Demonstrated

- Containerized multi-service architecture  
- Docker networking and service discovery  
- Environment-based configuration management  
- Database health checks and startup ordering  
- CI debugging using container logs  
- Fail-fast application startup patterns  
- Persistent storage using Docker volumes  

---

## 🔮 Future Enhancements

- [ ] Replace Flask development server with Gunicorn  
- [ ] Add automated tests to CI pipeline  
- [ ] Implement multi-stage CI (lint / build / test)  
- [ ] Deploy to cloud infrastructure (AWS / Azure)  
- [ ] Add Nginx reverse proxy  
- [ ] Convert CI to full CD pipeline with auto-deployment  

---

## 👨‍💻 Author

**Kushagra Agarwal**  
DevOps & Cloud Enthusiast

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub!
