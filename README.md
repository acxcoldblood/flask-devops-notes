
![CI](https://github.com/acxcoldblood/flask-devops-notes/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/acxcoldblood/flask-devops-notes/actions/workflows/deploy.yml/badge.svg)


# DevOps Notes Manager

A Flask-based CRUD web application for managing DevOps commands and notes, fully containerized using Docker and Docker Compose with a MySQL backend and a production-style CI pipeline using GitHub Actions.

---

## 🏗 Architecture Overview

```text
Browser
   |
   v
Nginx (Reverse Proxy, Rate Limiting)
   |
   v
Flask + Gunicorn (Docker container)
   |
   v
MySQL (Docker container)

```
## CI/CD pipeline

```text
┌──────────────┐
│   Git Push   │
└──────┬───────┘
       ↓
┌──────────────┐
│     CI       │
│ Docker Build │
│ Health Check │
└──────┬───────┘
       ↓
┌──────────────┐
│     CD       │
│  SSH → EC2   │
│ Docker Deploy│
└──────────────┘

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
├── .github/
│   └── workflows/
│       ├── ci.yml
        └── deploy.yml
         
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── db.py
│   └── config.py
├── nginx/
│   └── nginx.conf
├── scripts/
│   └── health_check.sh
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
├── templates/
│   ├── index.html
│   └── edit.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```text
DB_HOST=mysql
DB_USER=example_user
DB_PASSWORD=example_password
DB_NAME=example_db
MYSQL_ROOT_PASSWORD=example_root_password

```

📌 `.env` is ignored via `.gitignore`.  
📌 `.env.example` is committed for CI and local setup reference.

---

## ▶️ Run Locally (Docker)

### Prerequisites

- Docker
- Docker Compose

### Steps

git clone https://github.com/acxcoldblood/flask-devops-notes.git
cd flask-devops-notes

cp .env.example .env
docker compose up --build

Application will be available at:

```text
http://localhost

```

## (Nginx listens on port 80 and proxies to Flask internally)

## 🔄 CI Pipeline Overview

The GitHub Actions CI pipeline runs on every push to the `main` branch and performs:

- Checkout source code
- Create runtime `.env` from `.env.example`
- Build Docker images
- Start services using Docker Compose
- Wait for MySQL health check
- Start Flask via Gunicorn
- Validate application using `/health` endpoint
- Collect logs on failure
- Cleanly shut down containers

This ensures the application is buildable, runnable, and healthy on every commit.

---

## 🧪 Health Check Endpoint

The application exposes a lightweight health endpoint used by CI:

```text

GET /health

```

Response:

```text
200 OK
```

This avoids fragile checks against UI routes.

---

## 🔐 Nginx Security Hardening

- The reverse proxy includes:
- Per-IP rate limiting
- Explicit 429 responses for abuse
- Request body size limits (1MB)
- Backend isolation (Flask not exposed publicly)
- These protections prevent:
- Request floods
- Oversized payload abuse
- Direct access to application containers

## 🧠 DevOps Concepts Demonstrated

- Containerized multi-service architecture
- Reverse proxy pattern
- Docker networking and service discovery
- Environment-based configuration management
- Database health checks and startup ordering
- Gunicorn production server use
- CI-driven validation using real containers
- Safe, incremental deployments
- Safe, incremental deployments

---

## 🔮 Future Enhancements

- [ ] Authentication & authorization
- [ ] HTTPS with Let's Encrypt
- [ ] GitHub Actions CD (auto-deploy to EC2)
- [ ] Structured application logging
- [ ] Metrics & basic monitoring
- [ ] Database migrations
- [ ]Production backup strategy

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
