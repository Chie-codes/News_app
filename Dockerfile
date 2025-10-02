# Use Python slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient and other build tools
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Set environment variables for Django
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
