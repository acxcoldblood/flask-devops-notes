# Use official lightweight Python image
FROM python:3.11-alpine

# Set working directory inside container
WORKDIR /app

# Copy dependency file first (Docker cache optimization)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
