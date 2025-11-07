# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/pdfs templates

# Copy .env.example as template
COPY .env.example .env

# Expose Flask port
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app_flask.py
ENV PYTHONUNBUFFERED=1

# Run Flask application
CMD ["python", "app_flask.py"]
