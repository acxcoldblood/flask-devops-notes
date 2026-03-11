# DevOps Notes Manager

DevOps Notes Manager is a Flask application for storing DevOps notes and commands with authentication, categories/tags, API token access, password reset, and optional public note sharing.

## What You Can Replicate

- Local machine setup (Windows/Linux/macOS)
- EC2 production-style deployment with Docker Compose and RDS MySQL
- Health checks and validation steps

## Architecture

```text
Browser -> Nginx -> Flask (Gunicorn) -> MySQL
```

## Features

- User registration and login
- Password reset by email (SMTP)
- Note CRUD with categories, tags, rich text (sanitized)
- Public share links (`/s/<public_id>`)
- Profile settings + profile image upload
- API token auth (`X-API-Token`)
- Health endpoints: `/health`, `/api/health`

## Tech Stack

- Python 3.11
- Flask, Flask-Login, Flask-WTF
- Gunicorn
- MySQL 8
- Docker / Docker Compose
- Nginx

## Repo Layout

```text
app/                    Application code
templates/              HTML templates
static/                 CSS/JS/uploads
nginx/nginx.conf        Nginx reverse proxy config
scripts/migrate.py      Schema migration script
Dockerfile              App image build
docker-compose.prod.yml Production compose (web + nginx)
docker-compose.ci.yml   CI compose (web + mysql, no host ports)
Jenkinsfile.ci          CI pipeline
Jenkinsfile.cd          CD pipeline
```

## Prerequisites

### Local Machine

- Git
- Python 3.11+
- Docker Desktop (recommended for local MySQL)

### EC2 Deployment

- Ubuntu EC2 instance with Docker + Docker Compose plugin
- Security Group inbound rules:
  - `22/tcp` from your IP
  - `80/tcp` from Internet
  - `443/tcp` from Internet (only if you configure TLS)
- RDS MySQL instance reachable from EC2
- Domain name optional (required if you later add TLS)

## Environment Variables

Start from sample:

```bash
cp .env.example .env
```

Required for app startup:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT` (default `3306`)
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

Important in production compose:

- `IMAGE_TAG` (required by `docker-compose.prod.yml`)

Optional but recommended:

- `SESSION_COOKIE_SECURE=true` (for HTTPS)
- `REMEMBER_COOKIE_SECURE=true` (for HTTPS)
- `UPLOAD_MAX_MB`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SENDER`, `SMTP_USE_TLS`
- `RESET_TOKEN_MAX_AGE`

## Local Replication (Recommended)

This path runs Flask locally and MySQL in Docker so anyone can reproduce quickly.

### 1. Clone

```bash
git clone <your-repo-url>
cd Devops_notes_manager
```

### 2. Create `.env`

```bash
cp .env.example .env
```

Edit `.env` with at least:

```env
SECRET_KEY=replace_with_long_random_value
DB_HOST=127.0.0.1
DB_PORT=3307
DB_NAME=devops_notes
DB_USER=dnotes_user
DB_PASSWORD=dnotes_password
```

### 3. Start Local MySQL Container

```bash
docker run -d --name dnotes-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=devops_notes \
  -e MYSQL_USER=dnotes_user \
  -e MYSQL_PASSWORD=dnotes_password \
  -p 3307:3306 \
  mysql:8.0
```

### 4. Run the App

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m flask --app wsgi:app run --host 0.0.0.0 --port 5000
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi:app run --host 0.0.0.0 --port 5000
```

### 5. Verify

```bash
curl -fsS http://localhost:5000/health
curl -fsS http://localhost:5000/api/health
```

Open browser:

- `http://localhost:5000`

## EC2 Replication (Production-Style)

This path uses the existing `docker-compose.prod.yml` and pulls image `acxcoldblood/dnotes:${IMAGE_TAG}`.

### 1. Launch and Prepare EC2

SSH into EC2 and install Docker:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Copy Project Files to EC2

```bash
git clone <your-repo-url> dnotes
cd dnotes
```

### 3. Update Nginx Hostname

Edit `nginx/nginx.conf` and change:

- `server_name devvnotes.duckdns.org;`

to your domain or `_` (wildcard fallback) if no domain:

- `server_name _;`

### 4. Configure Production `.env`

Create `.env` in project root:

```env
IMAGE_TAG=latest
SECRET_KEY=replace_with_long_random_value

DB_HOST=<your-rds-endpoint>
DB_PORT=3306
DB_NAME=devops_notes
DB_USER=<db-user>
DB_PASSWORD=<db-password>

SESSION_COOKIE_SECURE=false
REMEMBER_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=Lax
REMEMBER_COOKIE_SAMESITE=Lax
UPLOAD_MAX_MB=2

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<smtp-user>
SMTP_PASSWORD=<smtp-password>
SMTP_SENDER=<from-email>
SMTP_USE_TLS=true
RESET_TOKEN_MAX_AGE=3600
```

Set `SESSION_COOKIE_SECURE=true` and `REMEMBER_COOKIE_SECURE=true` after TLS is configured.

### 5. Deploy

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 6. Verify on EC2

```bash
docker compose -f docker-compose.prod.yml ps
curl -fsS http://localhost/health
curl -fsS http://localhost/api/health
```

If port 80 is open in Security Group, app is reachable at:

- `http://<ec2-public-ip>/`

## API Quick Reference

Base URL: `/api`

- `GET /api/health` (public)
- `GET /api/notes` (token)
- `GET /api/notes/<id>` (token)
- `POST /api/notes` (token)
- `GET /api/categories` (token)

Auth header:

```text
X-API-Token: <token>
```

Generate/regenerate token from authenticated settings page (`/settings`).

## CI/CD Notes

- `Jenkinsfile.ci` builds/tests and pushes image tags to Docker Hub.
- `Jenkinsfile.cd` deploys selected branch builds to EC2 and runs health checks.

## Troubleshooting

- `RuntimeError: SECRET_KEY is required`:
  - Set `SECRET_KEY` in `.env`.
- DB connection failures:
  - Confirm `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
  - For RDS, allow inbound 3306 from EC2 Security Group.
- 502/Bad Gateway from Nginx:
  - Check app container logs:
  - `docker compose -f docker-compose.prod.yml logs --tail=200 web nginx`
- Forgot password email not sending:
  - Recheck SMTP vars and provider app-password requirements.
