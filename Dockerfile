# Use official lightweight Python image
FROM python:3.11-alpine

# Set working directory inside container
WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl


# Copy dependency file first (Docker cache optimization)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "wsgi:app"]

# Healthcheck to monitor application status
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1