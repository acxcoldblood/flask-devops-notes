# DevOps Notes Manager

DevOps Notes Manager is a Flask web app for storing DevOps commands and notes with tags, categories, and optional public sharing. The default deployment runs with Docker Compose using Nginx (reverse proxy) + Gunicorn (app server) + MySQL.

## Architecture

```text
Browser -> Nginx -> Flask (Gunicorn) -> MySQL
```

## Features

- CRUD notes per user
- Tags + categories
- Rich text notes (sanitized server-side)
- Optional public links for notes
- REST API with token authentication (header: `X-API-Token`)
- Docker + Docker Compose local deployment
- GitHub Actions CI workflow (container build + health check)

## Quick Start (Docker)

1. Create your env file:

```powershell
Copy-Item .env.example .env
```

2. Edit `.env` and set at least `SECRET_KEY` and the database values.

3. Start the stack:

```powershell
docker compose up --build
```

4. Open:

```text
http://localhost
```

MySQL is published on `localhost:3307` (container `3306`).

## Configuration

Key variables in `.env`:

- `SECRET_KEY` (required)
- `UPLOAD_MAX_MB` (default `2`)
- `SESSION_COOKIE_SECURE` (`true` in production/HTTPS)
- `REMEMBER_COOKIE_SECURE` (`true` in production/HTTPS)
- `SESSION_COOKIE_SAMESITE` (default `Lax`)
- `REMEMBER_COOKIE_SAMESITE` (default `Lax`)
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `DB_HOST` (default for Docker: `mysql`)
- `DB_PORT` (default `3306`)
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `SMTP_HOST` (default `smtp.gmail.com`)
- `SMTP_PORT` (default `587`)
- `SMTP_USER` (Gmail address)
- `SMTP_PASSWORD` (Gmail app password)
- `SMTP_SENDER` (From address)
- `SMTP_USE_TLS` (default `true`)
- `RESET_TOKEN_MAX_AGE` (seconds, default `3600`)

### Gmail SMTP Notes

Gmail requires an **App Password** if you have 2FA enabled. Create one in your Google Account, then set:

```
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## API

Base URL: `/api`

Authentication:

- Header: `X-API-Token: <token>`

Endpoints:

- `GET /api/health`
- `GET /api/notes`
- `POST /api/notes`
- `GET /api/notes/<id>`
- `GET /api/categories`

## Local Development (Without Docker)

You can run the Flask app locally, but you still need a MySQL instance and the correct env vars:

```powershell
python -m venv .venv
.venv\\Scripts\\pip install -r requirements.txt
.venv\\Scripts\\python -m flask --app wsgi:app run --host 0.0.0.0 --port 5000
```

## Security Notes

- `SECRET_KEY` is required for sessions and CSRF.
- Nginx rate limiting and security headers are configured in `nginx/nginx.conf`.
- Profile image uploads enforce extension + MIME type + size limits.
- Keep API tokens secret.

## Development Workflow

We use a branching strategy to separate development from production code:

- **`prod`**: The stable, production-ready branch. This is what runs in the live environment.
- **`dev`**: The active development branch. All new features and fixes should be committed here first.

### Workflow:

1.  **Develop**: Checkout the `dev` branch for your work.
    ```bash
    git checkout dev
    ```
2.  **Commit**: Make changes and commit them to `dev`.
    ```bash
    git add .
    git commit -m "Feature description"
    git push origin dev
    ```
3.  **Release**: To release changes to production, merge `dev` into `prod`.
    ```bash
    git checkout prod
    git merge dev
    git push origin prod
    ```

## Project Layout

```text
app/            Flask app (routes, auth, API, db)
templates/      Jinja templates
static/         Static assets (CSS/JS/uploads)
nginx/          Nginx reverse proxy config
migrations/     One-off migration scripts
.github/        GitHub Actions workflows
```
